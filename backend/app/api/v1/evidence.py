"""
NETRYX EVIDENCE — Evidence API Endpoints
Upload, download, verify integrity, list, and manage digital evidence.
Triggers the forensic-grade ingestion pipeline on upload.
"""

import hashlib
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user, require_role, UserRole
from app.core.events import event_bus
from app.core.config import get_settings
from app.models.user import User
from app.models.evidence import Evidence
from app.models.audit_log import AuditLog
from app.schemas.evidence import (
    EvidenceResponse,
    EvidenceUploadResponse,
    EvidenceListResponse,
    AnalysisResultResponse,
)

router = APIRouter(prefix="/evidence", tags=["Evidence"])
settings = get_settings()


def _classify_type(mime_type: str) -> str:
    """Classify evidence type from MIME type."""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type in (
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
    ):
        return "document"
    elif mime_type in ("message/rfc822", "application/mbox"):
        return "email"
    elif mime_type in ("text/csv", "text/x-log"):
        return "log"
    elif mime_type in ("application/x-pcap", "application/vnd.tcpdump.pcap"):
        return "network_capture"
    elif mime_type in ("application/zip", "application/x-tar", "application/gzip"):
        return "archive"
    elif mime_type == "application/octet-stream":
        return "binary"
    else:
        return "other"


@router.post("/upload", response_model=EvidenceUploadResponse, status_code=201)
async def upload_evidence(
    file: UploadFile = File(...),
    case_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload evidence file. Triggers the full forensic ingestion pipeline:
    1. Validation & security check
    2. Cryptographic hashing (SHA-256 + MD5 + SHA-1 + SHA-512)
    3. Metadata extraction
    4. Encrypted storage
    5. Evidence registration + audit trail
    6. Async analysis cascade (via event bus)
    """
    # Read file bytes
    file_bytes = await file.read()
    file_size = len(file_bytes)

    # Validate file size
    max_size = settings.MAX_EVIDENCE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file_size} bytes. Max: {max_size} bytes.",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Determine MIME type (from upload header for now; magic bytes in worker)
    mime_type = file.content_type or "application/octet-stream"

    # Compute cryptographic hashes
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    md5 = hashlib.md5(file_bytes).hexdigest()
    sha1 = hashlib.sha1(file_bytes).hexdigest()
    sha512 = hashlib.sha512(file_bytes).hexdigest()

    # Compute Shannon entropy
    entropy = _compute_entropy(file_bytes)

    # Check for duplicates in this case
    result = await db.execute(
        select(Evidence).where(
            Evidence.file_hash_sha256 == sha256,
            Evidence.case_id == case_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Evidence with hash {sha256[:16]}... already exists in this case.",
        )

    # Classify evidence type
    evidence_type = _classify_type(mime_type)

    # Generate storage path (content-addressed)
    storage_path = f"evidence/{sha256[:2]}/{sha256}"
    safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"

    # Upload to MinIO
    from app.services.storage import storage
    storage.upload_file(storage_path, file_bytes, mime_type)

    # Create evidence record
    evidence = Evidence(
        case_id=case_id,
        filename=safe_filename,
        original_filename=file.filename,
        mime_type=mime_type,
        type=evidence_type,
        file_size=file_size,
        file_hash_sha256=sha256,
        file_hash_md5=md5,
        file_hash_sha1=sha1,
        file_hash_sha512=sha512,
        storage_path=storage_path,
        entropy=entropy,
        analysis_status="pending",
        metadata={
            "original_filename": file.filename,
            "content_type": mime_type,
            "entropy": entropy,
        },
        uploaded_by=current_user.id,
    )
    db.add(evidence)
    await db.flush()

    # Create audit log entry
    db.add(AuditLog(
        action="EVIDENCE_UPLOADED",
        user_id=current_user.id,
        case_id=case_id,
        evidence_id=evidence.id,
        details={
            "filename": file.filename,
            "sha256": sha256,
            "size": file_size,
            "type": evidence_type,
            "storage": storage_path,
        },
        integrity_hash=AuditLog.compute_hash(
            "EVIDENCE_UPLOADED", str(current_user.id), {"sha256": sha256}
        ),
    ))
    await db.commit()

    payload = {
        "evidence_id": str(evidence.id),
        "case_id": case_id,
        "type": evidence_type,
        "mime_type": mime_type,
        "file_size": file_size,
        "sha256": sha256,
    }

    # Emit event to trigger real-time notifications
    await event_bus.emit("evidence.uploaded", payload)

    # Dispatch Celery task for async processing
    from app.workers.evidence_processor import process_upload_task
    process_upload_task.delay(payload)

    return EvidenceUploadResponse(
        id=str(evidence.id),
        filename=file.filename,
        file_hash_sha256=sha256,
        type=evidence_type,
        file_size=file_size,
        analysis_status="pending",
    )


@router.get("", response_model=EvidenceListResponse)
async def list_evidence(
    case_id: Optional[int] = None,
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List evidence with pagination and filtering."""
    query = select(Evidence)

    if case_id:
        query = query.where(Evidence.case_id == case_id)
    if type_filter:
        query = query.where(Evidence.type == type_filter)
    if status_filter:
        query = query.where(Evidence.analysis_status == status_filter)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Evidence.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return EvidenceListResponse(
        evidence=[
            EvidenceResponse(
                id=str(e.id),
                case_id=e.case_id,
                filename=e.filename,
                original_filename=e.original_filename,
                mime_type=e.mime_type,
                type=e.type,
                file_size=e.file_size,
                file_hash_sha256=e.file_hash_sha256,
                file_hash_md5=e.file_hash_md5,
                file_hash_sha1=e.file_hash_sha1,
                analysis_status=e.analysis_status,
                risk_score=e.risk_score,
                entropy=e.entropy,
                is_malicious=e.is_malicious,
                metadata=e.metadata or {},
                analysis_results=e.analysis_results or {},
                uploaded_by=str(e.uploaded_by),
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get evidence details by ID."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return EvidenceResponse(
        id=str(evidence.id),
        case_id=evidence.case_id,
        filename=evidence.filename,
        original_filename=evidence.original_filename,
        mime_type=evidence.mime_type,
        type=evidence.type,
        file_size=evidence.file_size,
        file_hash_sha256=evidence.file_hash_sha256,
        file_hash_md5=evidence.file_hash_md5,
        file_hash_sha1=evidence.file_hash_sha1,
        analysis_status=evidence.analysis_status,
        risk_score=evidence.risk_score,
        entropy=evidence.entropy,
        is_malicious=evidence.is_malicious,
        metadata=evidence.metadata or {},
        analysis_results=evidence.analysis_results or {},
        uploaded_by=str(evidence.uploaded_by),
        created_at=evidence.created_at,
        updated_at=evidence.updated_at,
    )


@router.get("/{evidence_id}/analysis", response_model=AnalysisResultResponse)
async def get_analysis_results(
    evidence_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed analysis results for evidence."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    from app.models.ioc import IOC
    from app.models.entity import Entity

    ioc_count = (await db.execute(
        select(func.count()).where(IOC.evidence_id == evidence.id)
    )).scalar() or 0

    entity_count = (await db.execute(
        select(func.count()).where(Entity.evidence_id == evidence.id)
    )).scalar() or 0

    return AnalysisResultResponse(
        evidence_id=str(evidence.id),
        status=evidence.analysis_status,
        results=evidence.analysis_results or {},
        risk_score=evidence.risk_score,
        ioc_count=ioc_count,
        entity_count=entity_count,
    )


@router.post("/{evidence_id}/reanalyze", status_code=202)
async def reanalyze_evidence(
    evidence_id: str,
    current_user: User = Depends(require_role(UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    """Trigger re-analysis of evidence. Analyst+ only."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence.analysis_status = "pending"
    evidence.analysis_results = {}
    await db.flush()

    await event_bus.emit("evidence.uploaded", {
        "evidence_id": str(evidence.id),
        "case_id": evidence.case_id,
        "type": evidence.type,
        "mime_type": evidence.mime_type,
        "reanalysis": True,
    })

    return {"message": "Re-analysis triggered", "evidence_id": str(evidence.id)}


# ── Helpers ──────────────────────────────────────────────────
def _compute_entropy(data: bytes) -> float:
    """Compute Shannon entropy of bytes. High entropy (>7.0) = encrypted/packed."""
    import math
    from collections import Counter

    if not data:
        return 0.0

    counts = Counter(data)
    length = len(data)
    entropy = 0.0

    for count in counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return round(entropy, 4)
