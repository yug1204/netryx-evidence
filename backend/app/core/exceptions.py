"""
NETRYX EVIDENCE — Custom Exception Hierarchy
Structured exceptions for consistent error handling across the platform.
"""

from fastapi import HTTPException, status


class NetryxException(Exception):
    """Base exception for all NETRYX errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ── Evidence Exceptions ──────────────────────────────────────
class EvidenceTooLargeError(NetryxException):
    def __init__(self, size: int, max_size: int):
        super().__init__(
            f"Evidence file size ({size} bytes) exceeds maximum ({max_size} bytes)",
            code="EVIDENCE_TOO_LARGE",
        )


class BlockedFileTypeError(NetryxException):
    def __init__(self, mime_type: str):
        super().__init__(
            f"File type '{mime_type}' is not allowed",
            code="BLOCKED_FILE_TYPE",
        )


class MalwareDetectedError(NetryxException):
    def __init__(self, virus_name: str):
        super().__init__(
            f"Malware detected: {virus_name}. File has been quarantined.",
            code="MALWARE_DETECTED",
        )


class EvidenceNotFoundError(NetryxException):
    def __init__(self, evidence_id: str):
        super().__init__(
            f"Evidence '{evidence_id}' not found",
            code="EVIDENCE_NOT_FOUND",
        )


class EvidenceIntegrityError(NetryxException):
    def __init__(self, evidence_id: str):
        super().__init__(
            f"Evidence '{evidence_id}' failed integrity check — possible tampering",
            code="EVIDENCE_INTEGRITY_FAILURE",
        )


# ── Auth Exceptions ──────────────────────────────────────────
class InvalidCredentialsError(NetryxException):
    def __init__(self):
        super().__init__("Invalid email or password", code="INVALID_CREDENTIALS")


class AccountLockedError(NetryxException):
    def __init__(self, until: str):
        super().__init__(
            f"Account locked until {until} due to repeated failed login attempts",
            code="ACCOUNT_LOCKED",
        )


class MFARequiredError(NetryxException):
    def __init__(self):
        super().__init__("MFA verification required", code="MFA_REQUIRED")


class MFAInvalidError(NetryxException):
    def __init__(self):
        super().__init__("Invalid MFA code", code="MFA_INVALID")


# ── Case Exceptions ──────────────────────────────────────────
class CaseNotFoundError(NetryxException):
    def __init__(self, case_id: int):
        super().__init__(f"Case #{case_id} not found", code="CASE_NOT_FOUND")


# ── Analysis Exceptions ─────────────────────────────────────
class AnalysisFailedError(NetryxException):
    def __init__(self, evidence_id: str, reason: str):
        super().__init__(
            f"Analysis failed for evidence '{evidence_id}': {reason}",
            code="ANALYSIS_FAILED",
        )


# ── Intelligence Exceptions ─────────────────────────────────
class ThreatIntelError(NetryxException):
    def __init__(self, provider: str, reason: str):
        super().__init__(
            f"Threat intelligence provider '{provider}' error: {reason}",
            code="THREAT_INTEL_ERROR",
        )


# ── HTTP Exception Converter ────────────────────────────────
def netryx_to_http(exc: NetryxException) -> HTTPException:
    """Convert a NetryxException to a FastAPI HTTPException."""
    status_map = {
        "INVALID_CREDENTIALS": status.HTTP_401_UNAUTHORIZED,
        "ACCOUNT_LOCKED": status.HTTP_403_FORBIDDEN,
        "MFA_REQUIRED": status.HTTP_403_FORBIDDEN,
        "MFA_INVALID": status.HTTP_401_UNAUTHORIZED,
        "EVIDENCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CASE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "EVIDENCE_TOO_LARGE": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        "BLOCKED_FILE_TYPE": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "MALWARE_DETECTED": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "EVIDENCE_INTEGRITY_FAILURE": status.HTTP_409_CONFLICT,
    }
    return HTTPException(
        status_code=status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        detail={"message": exc.message, "code": exc.code},
    )
