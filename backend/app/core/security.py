"""
NETRYX EVIDENCE — Security Module
JWT authentication, MFA (TOTP), password hashing, and RBAC.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from enum import Enum
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode
import io
import base64

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()

# ── Password Hashing ────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Bearer Token Scheme ─────────────────────────────────────
security_scheme = HTTPBearer()


# ── Role Enum ────────────────────────────────────────────────
class UserRole(str, Enum):
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    ADMIN = "admin"


# ── RBAC Permission Matrix ──────────────────────────────────
ROLE_HIERARCHY = {
    UserRole.INVESTIGATOR: 1,
    UserRole.ANALYST: 2,
    UserRole.ADMIN: 3,
}


# ── Password Operations ─────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Token Operations ────────────────────────────────────
def create_access_token(
    user_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),  # Unique token ID for blacklisting
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a signed JWT refresh token with longer expiry."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── MFA (TOTP) Operations ───────────────────────────────────
def generate_mfa_secret() -> str:
    """Generate a new TOTP secret for MFA enrollment."""
    return pyotp.random_base32()


def get_mfa_provisioning_uri(secret: str, email: str) -> str:
    """Generate a provisioning URI for authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.MFA_ISSUER)


def generate_mfa_qr_code(provisioning_uri: str) -> str:
    """Generate a QR code image as base64 for MFA setup."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify a TOTP code with a 30-second window (±1 step tolerance)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


# ── Authentication Dependencies ─────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    FastAPI dependency: Extract and validate the current user from JWT.
    Returns the User ORM object.
    """
    from app.models.user import User  # Lazy import to avoid circular deps

    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to failed login attempts.",
        )

    return user


def require_role(minimum_role: UserRole):
    """
    FastAPI dependency factory: Require a minimum role level.
    Usage: Depends(require_role(UserRole.ANALYST))
    """

    async def role_checker(current_user=Depends(get_current_user)):
        user_level = ROLE_HIERARCHY.get(UserRole(current_user.role), 0)
        required_level = ROLE_HIERARCHY.get(minimum_role, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Requires {minimum_role.value} or higher.",
            )
        return current_user

    return role_checker
