"""
NETRYX EVIDENCE — Evidence Model
Digital evidence with cryptographic hashing (6 algorithms), encryption tracking,
metadata (JSONB), analysis results, and chain-of-custody support.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Boolean, DateTime, Text, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)

    # File identification
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # image, document, email, log, network_capture, binary, archive, url, other
    file_size = Column(BigInteger, nullable=False)

    # Cryptographic hashes (6 algorithms for maximum interoperability)
    file_hash_sha256 = Column(String(64), nullable=False, index=True)
    file_hash_md5 = Column(String(32), nullable=True)
    file_hash_sha1 = Column(String(40), nullable=True)
    file_hash_sha512 = Column(String(128), nullable=True)
    file_hash_ssdeep = Column(Text, nullable=True)   # Fuzzy hash for similarity
    file_hash_tlsh = Column(Text, nullable=True)      # Locality-sensitive hash

    # Storage
    storage_path = Column(Text, nullable=False)
    encryption_key_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadata & Analysis
    metadata = Column(JSONB, default=dict)
    analysis_status = Column(String(50), default="pending")  # pending, processing, completed, failed, quarantined
    analysis_results = Column(JSONB, default=dict)

    # Risk
    risk_score = Column(Integer, default=0)
    entropy = Column(Float, nullable=True)  # Shannon entropy
    is_malicious = Column(Boolean, default=False)

    # Audit
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    case = relationship("Case", back_populates="evidence_items")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    iocs = relationship("IOC", back_populates="evidence", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="evidence")
    embeddings = relationship("EvidenceEmbedding", back_populates="evidence", cascade="all, delete-orphan")
    image_embeddings = relationship("ImageEmbedding", back_populates="evidence", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Evidence {self.filename} ({self.type}) [{self.analysis_status}]>"
