"""
NETRYX EVIDENCE — Embedding Models
Vector embeddings for semantic search using pgvector.
- EvidenceEmbedding: Text chunks from documents/emails/logs (1536-dim, OpenAI)
- ImageEmbedding: CLIP visual embeddings from images (768-dim)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, DateTime, Text, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class EvidenceEmbedding(Base):
    """Text chunk embeddings for RAG (Retrieval-Augmented Generation)."""
    __tablename__ = "evidence_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Chunk data
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, default=dict)  # Page number, section, source

    # Vector embedding (OpenAI text-embedding-3-small = 1536 dimensions)
    embedding = Column(Vector(1536), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evidence = relationship("Evidence", back_populates="embeddings")

    def __repr__(self):
        return f"<EvidenceEmbedding evidence={self.evidence_id} chunk={self.chunk_index}>"


class ImageEmbedding(Base):
    """CLIP visual embeddings for image similarity search."""
    __tablename__ = "image_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Vector embedding (CLIP ViT-L/14 = 768 dimensions)
    embedding = Column(Vector(768), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evidence = relationship("Evidence", back_populates="image_embeddings")

    def __repr__(self):
        return f"<ImageEmbedding evidence={self.evidence_id}>"
