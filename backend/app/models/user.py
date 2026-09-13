"""
NETRYX EVIDENCE — User Model
Supports JWT auth, MFA (TOTP), RBAC roles, account lockout.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False, default="investigator")
    password_hash = Column(Text, nullable=False)

    # MFA
    mfa_secret = Column(Text, nullable=True)
    mfa_enabled = Column(Boolean, default=False)

    # Account status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

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
    cases = relationship("Case", back_populates="creator", foreign_keys="Case.created_by")
    assigned_cases = relationship("Case", back_populates="assignee", foreign_keys="Case.assigned_to")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
