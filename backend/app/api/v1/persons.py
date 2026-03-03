"""
Spectra — Person API (v1) — Phase 8 extensions
GET /api/v1/persons — paginated list of synthetic persons.
GET /api/v1/persons/{id} — single person detail.
GET /api/v1/persons/{id}/summary — Claude AI summary.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.anomaly import AnomalyRecord, EntityType
from app.models.event import Event
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonResponse
from app.services.ai_summary_service import generate_person_summary

router = APIRouter()

_MAX_LIMIT = 100


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, description="Case-insensitive filter on fake_name"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[PersonResponse]:
    """Return a paginated list of synthetic persons.  Requires Bearer JWT."""
    if limit > _MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"limit must be ≤ {_MAX_LIMIT}",
        )

    stmt = select(Person)
    if search:
        stmt = stmt.where(Person.fake_name.ilike(f"%{search}%"))
    stmt = stmt.offset(offset).limit(limit).order_by(Person.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PersonResponse:
    """Return a single synthetic person by ID.  Requires Bearer JWT."""
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person


@router.get("/{person_id}/summary")
async def get_person_summary(
    person_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """
    Generate an AI intelligence analyst summary for a synthetic person.
    Calls Claude Sonnet via the ai_summary_service.
    Requires Bearer JWT.
    """
    # Load person
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    # Load all events for this person (actor OR target)
    events_result = await db.execute(
        select(Event)
        .where(or_(Event.actor_id == person_id, Event.target_id == person_id))
        .order_by(Event.occurred_at.desc())
        .limit(50)
    )
    events = list(events_result.scalars().all())

    # Load anomaly records related to this person's events
    if events:
        event_ids = [e.id for e in events]
        anomaly_result = await db.execute(
            select(AnomalyRecord)
            .where(
                AnomalyRecord.entity_id.in_(event_ids),
                AnomalyRecord.entity_type == EntityType.event,
            )
        )
        anomalies = list(anomaly_result.scalars().all())
    else:
        anomalies = []

    # Generate summary with Claude
    summary = await generate_person_summary(person, events, anomalies)

    return {"summary": summary, "person_id": person_id}
