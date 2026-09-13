"""
NETRYX EVIDENCE — Audit Log Model
Tamper-proof, hash-chained audit trail for forensic chain of custody.
Each entry includes the hash of the previous entry (blockchain-inspired).
"""

import uuid
import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, BigInteger, DateTime, Text, Integer, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Hash chain (tamper detection)
    previous_hash = Column(String(64), nullable=True)  # SHA-256 of previous entry
    integrity_hash = Column(String(64), nullable=False)  # SHA-256 of this entry

    # Action details
    action = Column(String(100), nullable=False, index=True)
    # Actions: EVIDENCE_UPLOADED, EVIDENCE_DOWNLOADED, EVIDENCE_DELETED,
    #          CASE_CREATED, CASE_UPDATED, CASE_CLOSED,
    #          USER_LOGIN, USER_LOGIN_FAILED, USER_MFA_ENABLED,
    #          ANALYSIS_STARTED, ANALYSIS_COMPLETED,
    #          IOC_CREATED, REPORT_GENERATED, etc.

    # References
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Details
    details = Column(JSONB, default=dict)

    # Request context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    @staticmethod
    def compute_hash(
        action: str,
        user_id: str,
        details: dict,
        previous_hash: str = "",
        timestamp: str = "",
    ) -> str:
        """
        Compute SHA-256 integrity hash for this audit entry.
        Includes the previous hash to create an unbreakable chain.
        """
        content = json.dumps(
            {
                "action": action,
                "user_id": str(user_id) if user_id else "",
                "details": details,
                "previous_hash": previous_hash,
                "timestamp": timestamp,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def __repr__(self):
        return f"<AuditLog #{self.id}: {self.action}>"
