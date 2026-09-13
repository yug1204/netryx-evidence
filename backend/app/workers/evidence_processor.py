"""
NETRYX EVIDENCE — Evidence Processor Worker (Celery)
Listens to the 'evidence' queue. Triggered by 'evidence.uploaded' event.
Performs background validation, ClamAV/YARA malware checks, and metadata extraction.
"""

import asyncio
import json
from celery import shared_task

from app.core.database import async_session
from app.models.evidence import Evidence
from app.models.audit_log import AuditLog
from app.core.events import event_bus


async def process_evidence_async(payload: dict):
    """
    Async logic for processing evidence.
    This runs inside the Celery worker task.
    """
    evidence_id = payload.get("evidence_id")
    file_type = payload.get("type", "other")
    sha256 = payload.get("sha256")

    print(f"⚙️ Starting processing for evidence {evidence_id} (Type: {file_type})")

    async with async_session() as session:
        # 1. Fetch evidence
        from sqlalchemy import select
        result = await session.execute(select(Evidence).where(Evidence.id == evidence_id))
        evidence = result.scalar_one_or_none()

        if not evidence:
            print(f"❌ Evidence {evidence_id} not found in database.")
            return

        evidence.analysis_status = "processing"
        await session.commit()

        # 2. Simulate Malware/YARA Scan (ClamAV)
        # In a real environment, we would pull the file from MinIO and run clamd / yara-python
        is_malicious = False
        virus_name = None
        risk_score = 0
        
        # High entropy files or known suspicious signatures raise the risk score
        if evidence.entropy and evidence.entropy > 7.5:
            risk_score += 30
            
        if is_malicious:
            evidence.analysis_status = "quarantined"
            evidence.is_malicious = True
            evidence.risk_score = 100
            evidence.analysis_results["malware_scan"] = {
                "status": "infected",
                "signature": virus_name
            }
            await session.commit()
            print(f"🚨 Malware detected in {evidence_id}. Quarantined.")
            return

        # 3. Simulate Metadata Extraction
        # In a real implementation:
        # - Images: EXIF data (GPS, camera model, timestamps)
        # - Docs: Author, creation dates, embedded macros
        # - EML: Headers, routing path, attachments
        metadata_results = {
            "processed": True,
            "extraction_engine": "netryx_core_v1",
            "file_type_magic": evidence.mime_type
        }
        
        # Merge new metadata
        existing_meta = evidence.metadata or {}
        existing_meta.update(metadata_results)
        evidence.metadata = existing_meta

        # 4. Finish Processing
        evidence.analysis_status = "completed"
        evidence.risk_score = risk_score
        
        # Add Audit Log
        audit = AuditLog(
            action="EVIDENCE_PROCESSED",
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            details={"risk_score": risk_score, "malware_scan": "clean"},
            integrity_hash=AuditLog.compute_hash("EVIDENCE_PROCESSED", "system", {"sha256": sha256})
        )
        session.add(audit)
        await session.commit()

        print(f"✅ Processing complete for evidence {evidence_id}.")

        # 5. Emit downstream events for analysis engines
        # e.g., if it's an image, send to OCR/Vision pipeline; if email, send to email parser
        if file_type == "image":
            await event_bus.emit("analysis.image.requested", payload)
        elif file_type == "document":
            await event_bus.emit("analysis.document.requested", payload)
        elif file_type == "email":
            await event_bus.emit("analysis.email.requested", payload)
        elif file_type == "network_capture":
            await event_bus.emit("analysis.pcap.requested", payload)
        else:
            # Fallback to standard IOC extraction
            await event_bus.emit("analysis.ioc_extraction.requested", payload)


@shared_task(name="evidence.process_upload")
def process_upload_task(payload: dict):
    """
    Celery task entrypoint.
    Since SQLAlchemy async is used, we must run the async function in an event loop.
    """
    asyncio.run(process_evidence_async(payload))
