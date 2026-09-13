"""
NETRYX EVIDENCE — Relationship Model
Links between entities discovered by the correlation engine.
Becomes edges in the Neo4j investigation graph.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)

    # Linked entities
    source_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    target_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)

    # Relationship details
    relation_type = Column(String(100), nullable=False)  # resolves_to, sent_from, contains, attached, connects_to, etc.
    confidence = Column(Float, default=0.0)
    evidence_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Which evidence supports this link
    attributes = Column(JSONB, default=dict)
    discovered_by = Column(String(100), nullable=True)  # correlation_engine, manual, analysis

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="relationships_list")
    source_entity = relationship("Entity", foreign_keys=[source_entity_id])
    target_entity = relationship("Entity", foreign_keys=[target_entity_id])

    def __repr__(self):
        return f"<Relationship {self.source_entity_id} --[{self.relation_type}]--> {self.target_entity_id}>"
