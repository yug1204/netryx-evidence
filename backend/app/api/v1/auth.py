"""
NETRYX EVIDENCE — Auth API Endpoints
Registration, login (with MFA challenge), MFA setup/verify, token refresh.
Includes account lockout after failed attempts.
"""

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_mfa_secret,
    get_mfa_provisioning_uri,
    generate_mfa_qr_code,
    verify_mfa_code,
    get_current_user,
)
from app.core.config import get_settings
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    MFARequiredResponse,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    RefreshRequest,
    RefreshResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
    )
    db.add(user)
    await db.flush()

    return RegisterResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
    )


@router.post("/login")
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.
    If MFA is enabled, returns a temporary MFA token instead of access tokens.
    """
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check account lock
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until.isoformat()}",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + LOCKOUT_DURATION
            user.failed_login_attempts = 0

        # Audit log
        db.add(AuditLog(
            action="USER_LOGIN_FAILED",
            user_id=user.id,
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent"),
            details={"reason": "invalid_password", "attempts": user.failed_login_attempts},
            integrity_hash=AuditLog.compute_hash("USER_LOGIN_FAILED", str(user.id), {}),
        ))
        await db.flush()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Reset failed attempts on successful password
    user.failed_login_attempts = 0
    user.locked_until = None

    # Check if MFA is required
    if user.mfa_enabled and user.mfa_secret:
        # Issue temporary MFA token
        mfa_token = create_access_token(
            user_id=str(user.id),
            role=user.role,
            expires_delta=timedelta(minutes=5),
        )
        return MFARequiredResponse(mfa_token=mfa_token)

    # No MFA — issue tokens directly
    user.last_login = datetime.now(timezone.utc)
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

    # Audit log
    db.add(AuditLog(
        action="USER_LOGIN",
        user_id=user.id,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        details={"mfa": False},
        integrity_hash=AuditLog.compute_hash("USER_LOGIN", str(user.id), {"mfa": False}),
    ))

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfile(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            mfa_enabled=user.mfa_enabled,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable MFA for the current user. Returns QR code for authenticator app."""
    secret = generate_mfa_secret()
    provisioning_uri = get_mfa_provisioning_uri(secret, current_user.email)
    qr_code = generate_mfa_qr_code(provisioning_uri)

    # Store secret (will be confirmed on first successful verification)
    current_user.mfa_secret = secret
    await db.flush()

    return MFASetupResponse(
        secret=secret,
        provisioning_uri=provisioning_uri,
        qr_code_base64=qr_code,
    )


@router.post("/mfa/verify", response_model=MFAVerifyResponse)
async def mfa_verify(
    request: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify MFA code. Used for both setup confirmation and login verification."""
    if request.mfa_token:
        # Login flow — verify the temporary MFA token
        payload = decode_token(request.mfa_token)
        user_id = payload.get("sub")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.mfa_secret:
            raise HTTPException(status_code=400, detail="Invalid MFA state")

        if not verify_mfa_code(user.mfa_secret, request.code):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

        # Issue full tokens
        user.last_login = datetime.now(timezone.utc)
        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        return MFAVerifyResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            message="MFA verification successful",
        )

    raise HTTPException(status_code=400, detail="mfa_token is required for login verification")


@router.post("/mfa/confirm")
async def mfa_confirm(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm MFA setup by verifying the first code from the authenticator app."""
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up. Call /mfa/setup first.")

    if not verify_mfa_code(current_user.mfa_secret, request.code):
        raise HTTPException(status_code=401, detail="Invalid MFA code. Try again.")

    current_user.mfa_enabled = True
    await db.flush()

    return {"success": True, "message": "MFA enabled successfully"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh an expired access token using a valid refresh token."""
    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(str(user.id), user.role)

    return RefreshResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserProfile(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        mfa_enabled=current_user.mfa_enabled,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
