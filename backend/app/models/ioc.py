"""
NETRYX EVIDENCE — IOC (Indicator of Compromise) Model
Stores extracted IOCs with type classification, risk scoring,
confidence levels, enrichment data from threat intel sources,
and sighting tracking.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class IOC(Base):
    __tablename__ = "iocs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=True)

    # IOC identification
    type = Column(String(50), nullable=False)  # ipv4, ipv6, domain, url, email, md5, sha1, sha256, etc.
    value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=False, index=True)  # Lowercased, defanged, etc.

    # Risk assessment
    risk = Column(String(20), default="unknown")  # critical, high, medium, low, info, unknown
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0

    # Tracking
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sighting_count = Column(Integer, default=1)

    # Metadata
    tags = Column(ARRAY(String), default=list)
    enrichment = Column(JSONB, default=dict)  # VirusTotal, MISP, Shodan results
    source = Column(String(100), nullable=True)  # Which analysis module found this
    is_whitelisted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="iocs")
    evidence = relationship("Evidence", back_populates="iocs")

    def __repr__(self):
        return f"<IOC {self.type}:{self.value} ({self.risk})>"
