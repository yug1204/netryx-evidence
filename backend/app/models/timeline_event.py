"""
NETRYX EVIDENCE — Timeline Event Model
Temporal events extracted from all evidence types.
Supports precision tracking, clustering, and entity/IOC linking.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, Text, Integer, ForeignKey, ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=True)

    # Event details
    event_type = Column(String(100), nullable=False)  # email.received, url.accessed, file.downloaded, connection.detected, etc.
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    timestamp_precision = Column(String(20), default="second")  # year, month, day, hour, minute, second, millisecond
    timezone_name = Column(String(50), default="UTC")

    # Context
    source = Column(Text, nullable=True)  # Which evidence/module produced this event
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="info")  # critical, high, medium, low, info

    # Linked entities and IOCs
    entity_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    ioc_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)

    # Clustering (assigned by temporal analysis)
    cluster_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="timeline_events")

    def __repr__(self):
        return f"<TimelineEvent {self.event_type} @ {self.timestamp}>"
