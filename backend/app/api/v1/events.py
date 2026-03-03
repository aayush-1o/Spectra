"""
Spectra — Events API (v1)
GET /api/v1/events — paginated, filterable list of synthetic events.

Phase 8: Added optional person_id query param to filter events where
         actor_id == person_id OR target_id == person_id.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.event import Event, EventType
from app.models.user import User
from app.schemas.event import EventResponse

router = APIRouter()

_MAX_LIMIT = 200


@router.get("", response_model=list[EventResponse])
async def list_events(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    type: str | None = Query(default=None, description="Filter by event_type enum value"),
    from_date: datetime | None = Query(default=None, description="Only events on or after this datetime"),
    to_date: datetime | None = Query(default=None, description="Only events on or before this datetime"),
    person_id: str | None = Query(default=None, description="Filter events where actor_id=id OR target_id=id"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[EventResponse]:
    """Return a paginated, optionally filtered list of synthetic events.  Requires Bearer JWT."""
    if limit > _MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"limit must be ≤ {_MAX_LIMIT}",
        )

    stmt = select(Event)

    if type is not None:
        try:
            event_type_enum = EventType(type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid event type '{type}'. Valid values: {[e.value for e in EventType]}",
            )
        stmt = stmt.where(Event.event_type == event_type_enum)

    if from_date is not None:
        stmt = stmt.where(Event.occurred_at >= from_date)

    if to_date is not None:
        stmt = stmt.where(Event.occurred_at <= to_date)

    # Phase 8: filter by person participation (actor OR target)
    if person_id is not None:
        stmt = stmt.where(
            or_(Event.actor_id == person_id, Event.target_id == person_id)
        )

    stmt = stmt.offset(offset).limit(limit).order_by(Event.occurred_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()
