"""
NETRYX EVIDENCE — Case Schemas
Request/response schemas for case management.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500, examples=["Suspicious Phishing Campaign"])
    description: Optional[str] = Field(None, max_length=5000)
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")
    tags: list[str] = Field(default_factory=list)
    assigned_to: Optional[str] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    status: Optional[str] = Field(None, pattern="^(open|under_investigation|pending_review|closed|archived)$")
    tags: Optional[list[str]] = None
    assigned_to: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    risk_score: int
    tags: list[str]
    assigned_to: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    # Counts (populated by query)
    evidence_count: int = 0
    ioc_count: int = 0
    entity_count: int = 0
    event_count: int = 0

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    cases: list[CaseResponse]
    total: int
    page: int
    page_size: int
