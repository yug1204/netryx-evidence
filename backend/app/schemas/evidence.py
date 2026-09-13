"""
NETRYX EVIDENCE — Evidence Schemas
Request/response schemas for evidence management.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class EvidenceResponse(BaseModel):
    id: str
    case_id: int
    filename: str
    original_filename: str
    mime_type: str
    type: str
    file_size: int

    # Hashes
    file_hash_sha256: str
    file_hash_md5: Optional[str] = None
    file_hash_sha1: Optional[str] = None

    # Analysis
    analysis_status: str
    risk_score: int
    entropy: Optional[float] = None
    is_malicious: bool
    metadata: dict = {}
    analysis_results: dict = {}

    # Audit
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvidenceUploadResponse(BaseModel):
    id: str
    filename: str
    file_hash_sha256: str
    type: str
    file_size: int
    analysis_status: str
    message: str = "Evidence uploaded successfully. Analysis pipeline started."


class EvidenceListResponse(BaseModel):
    evidence: list[EvidenceResponse]
    total: int
    page: int
    page_size: int


class ChainOfCustodyEntry(BaseModel):
    action: str
    user_name: str
    timestamp: datetime
    details: dict
    ip_address: Optional[str] = None
    integrity_hash: str


class ChainOfCustodyResponse(BaseModel):
    evidence_id: str
    filename: str
    file_hash: str
    chain: list[ChainOfCustodyEntry]
    chain_valid: bool  # True if no hash breaks detected


class AnalysisResultResponse(BaseModel):
    evidence_id: str
    status: str
    results: dict[str, Any]  # Module name → results
    risk_score: int
    ioc_count: int
    entity_count: int
    completed_at: Optional[datetime] = None
