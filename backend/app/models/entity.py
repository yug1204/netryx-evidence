"""
NETRYX EVIDENCE — Entity Model
Entities extracted from evidence: persons, organizations, IPs, domains, etc.
Used as nodes in the investigation graph (Neo4j).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Float, DateTime, Text, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=True)

    # Entity identification
    type = Column(String(50), nullable=False)  # person, organization, location, domain, ip_address, email_address, file, url, device, account, software, vulnerability
    name = Column(Text, nullable=False)
    normalized_name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Attributes & confidence
    attributes = Column(JSONB, default=dict)  # Type-specific attributes
    confidence = Column(Float, default=0.0)
    source = Column(String(100), nullable=True)  # NER, regex, manual, etc.

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="entities")
    evidence = relationship("Evidence", back_populates="entities")

    def __repr__(self):
        return f"<Entity {self.type}:{self.name}>"
