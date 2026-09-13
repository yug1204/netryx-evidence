"""
NETRYX EVIDENCE — Auth Schemas
Request/response schemas for authentication, registration, MFA.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Registration ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["Agent 01"])
    email: EmailStr = Field(..., examples=["investigator@netryx.io"])
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="investigator", pattern="^(investigator|analyst|admin)$")


class RegisterResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    message: str = "Account created successfully"


# ── Login ────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserProfile"


class MFARequiredResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str  # Temporary token to complete MFA
    message: str = "MFA verification required"


# ── MFA ──────────────────────────────────────────────────────
class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
    qr_code_base64: str
    message: str = "Scan the QR code with your authenticator app"


class MFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    mfa_token: Optional[str] = None  # For login flow


class MFAVerifyResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: str


# ── Token Refresh ────────────────────────────────────────────
class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ── User Profile ─────────────────────────────────────────────
class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    mfa_enabled: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
