"""
NETRYX EVIDENCE — Cases API Endpoints
Full CRUD for investigation cases with pagination, filtering, and role-based access.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.security import get_current_user, require_role, UserRole
from app.models.user import User
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.ioc import IOC
from app.models.entity import Entity
from app.models.timeline_event import TimelineEvent
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
)

router = APIRouter(prefix="/cases", tags=["Cases"])


def _build_case_response(case: Case, counts: dict) -> CaseResponse:
    """Convert ORM model to response schema with counts."""
    return CaseResponse(
        id=case.id,
        title=case.title,
        description=case.description,
        priority=case.priority,
        status=case.status,
        risk_score=case.risk_score,
        tags=case.tags or [],
        assigned_to=str(case.assigned_to) if case.assigned_to else None,
        created_by=str(case.created_by),
        created_at=case.created_at,
        updated_at=case.updated_at,
        closed_at=case.closed_at,
        evidence_count=counts.get("evidence", 0),
        ioc_count=counts.get("ioc", 0),
        entity_count=counts.get("entity", 0),
        event_count=counts.get("event", 0),
    )


@router.get("", response_model=CaseListResponse)
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List cases with pagination and filtering."""
    query = select(Case)

    # Investigators can only see their own cases
    if current_user.role == "investigator":
        query = query.where(
            (Case.created_by == current_user.id) | (Case.assigned_to == current_user.id)
        )

    # Apply filters
    if status_filter:
        query = query.where(Case.status == status_filter)
    if priority:
        query = query.where(Case.priority == priority)
    if search:
        query = query.where(Case.title.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Case.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    cases = result.scalars().all()

    # Get counts for each case
    case_responses = []
    for case in cases:
        counts = await _get_case_counts(db, case.id)
        case_responses.append(_build_case_response(case, counts))

    return CaseListResponse(
        cases=case_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CaseResponse, status_code=201)
async def create_case(
    request: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new investigation case."""
    case = Case(
        title=request.title,
        description=request.description,
        priority=request.priority,
        tags=request.tags,
        created_by=current_user.id,
        assigned_to=request.assigned_to if request.assigned_to else current_user.id,
    )
    db.add(case)
    await db.flush()

    return _build_case_response(case, {})


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get case details by ID."""
    case = await _get_case_or_404(db, case_id, current_user)
    counts = await _get_case_counts(db, case_id)
    return _build_case_response(case, counts)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    request: CaseUpdate,
    current_user: User = Depends(require_role(UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    """Update case details. Requires Analyst or Admin role."""
    case = await _get_case_or_404(db, case_id, current_user)

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    # Handle status transitions
    if request.status == "closed" and not case.closed_at:
        case.closed_at = datetime.now(timezone.utc)
    elif request.status and request.status != "closed":
        case.closed_at = None

    await db.flush()
    counts = await _get_case_counts(db, case_id)
    return _build_case_response(case, counts)


@router.delete("/{case_id}", status_code=204)
async def delete_case(
    case_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Delete a case. Admin only. Cascades to all related data."""
    case = await _get_case_or_404(db, case_id, current_user)
    await db.delete(case)


# ── Reports ──────────────────────────────────────────────────
@router.post("/{case_id}/report", status_code=202)
async def generate_case_report(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers background generation of a forensic PDF report.
    """
    await _get_case_or_404(db, case_id, current_user)
    
    from app.workers.report_worker import generate_report_task
    generate_report_task.delay({
        "case_id": case_id,
        "requester_id": current_user.id
    })
    
    return {"message": "Report generation started."}

# ── Helpers ──────────────────────────────────────────────────
async def _get_case_or_404(db: AsyncSession, case_id: int, user: User) -> Case:
    """Get a case or raise 404."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail=f"Case #{case_id} not found")

    # Investigators can only see their own cases
    if user.role == "investigator" and case.created_by != user.id and case.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return case


async def _get_case_counts(db: AsyncSession, case_id: int) -> dict:
    """Get aggregate counts for a case."""
    evidence_count = (await db.execute(
        select(func.count()).where(Evidence.case_id == case_id)
    )).scalar() or 0

    ioc_count = (await db.execute(
        select(func.count()).where(IOC.case_id == case_id)
    )).scalar() or 0

    entity_count = (await db.execute(
        select(func.count()).where(Entity.case_id == case_id)
    )).scalar() or 0

    event_count = (await db.execute(
        select(func.count()).where(TimelineEvent.case_id == case_id)
    )).scalar() or 0

    return {
        "evidence": evidence_count,
        "ioc": ioc_count,
        "entity": entity_count,
        "event": event_count,
    }
