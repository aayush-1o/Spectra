"""
Spectra — NL Search API (v1)
POST /api/v1/search/nl — natural language person search powered by Claude.

⚠️ All data is synthetic. No real persons are searched.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.event import Event, EventType
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonResponse
from app.services.nl_search_service import parse_nl_query

logger = logging.getLogger(__name__)
router = APIRouter()


class NLSearchRequest(BaseModel):
    query: str


class NLSearchResponse(BaseModel):
    persons: list[PersonResponse]
    total: int
    query: str
    filters_applied: dict


@router.post("/nl", response_model=NLSearchResponse)
async def nl_search(
    body: NLSearchRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> NLSearchResponse:
    """
    Parse a natural language query with Claude and return matching synthetic persons.
    Requires Bearer JWT.
    """
    if not body.query.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query cannot be empty",
        )

    # ── Parse intent with Claude ───────────────────────────────────────────────
    filters = await parse_nl_query(body.query)
    logger.info("NL search filters: %s", filters)

    # ── Build SQLAlchemy query from filters ────────────────────────────────────
    stmt = select(Person).distinct()

    # Filters that require joining events
    needs_event_join = any(k in filters for k in [
        "min_transfer_usd", "max_transfer_usd", "after_hour", "before_hour", "event_type"
    ])

    if needs_event_join:
        # Join to events where person is actor or target
        event_conditions = [
            or_(Event.actor_id == Person.id, Event.target_id == Person.id)
        ]

        # Event type filter
        if "event_type" in filters:
            try:
                et = EventType(filters["event_type"])
                event_conditions.append(Event.event_type == et)
            except ValueError:
                pass

        # Transfer amount filters (on event metadata — use subquery pattern)
        # We use a simpler approach: get matching event person_ids, then filter persons
        # Transfer amount filters are handled post-query (Python-side)
        # because metadata_ is a JSONB field that's harder to push into SQL reliably.

        # Hour-of-day filters — apply via EXTRACT
        hour_conditions = []
        if "after_hour" in filters:
            try:
                from sqlalchemy import extract
                hour_conditions.append(extract("hour", Event.occurred_at) >= int(filters["after_hour"]))
            except (ValueError, TypeError):
                pass
        if "before_hour" in filters:
            try:
                from sqlalchemy import extract
                hour_conditions.append(extract("hour", Event.occurred_at) <= int(filters["before_hour"]))
            except (ValueError, TypeError):
                pass

        # Join
        stmt = stmt.join(
            Event,
            or_(Event.actor_id == Person.id, Event.target_id == Person.id),
        )
        for cond in hour_conditions:
            stmt = stmt.where(cond)
        if "event_type" in filters:
            try:
                et = EventType(filters["event_type"])
                stmt = stmt.where(Event.event_type == et)
            except ValueError:
                pass

    # Person-level filters (no join needed)
    if "occupation" in filters and filters["occupation"]:
        stmt = stmt.where(Person.occupation.ilike(f"%{filters['occupation']}%"))

    if "nationality" in filters and filters["nationality"]:
        stmt = stmt.where(Person.fake_nationality.ilike(f"%{filters['nationality']}%"))

    if "has_alias" in filters and filters["has_alias"]:
        stmt = stmt.where(Person.fake_alias.isnot(None))

    if "min_risk_score" in filters:
        try:
            stmt = stmt.where(Person.risk_score >= float(filters["min_risk_score"]))
        except (ValueError, TypeError):
            pass

    stmt = stmt.limit(50)
    result = await db.execute(stmt)
    persons = result.scalars().all()

    # Post-query filter for transfer amount (JSON metadata — can't easily do in SQL)
    if "min_transfer_usd" in filters or "max_transfer_usd" in filters:
        person_ids = {p.id for p in persons}
        min_t = float(filters.get("min_transfer_usd", 0))
        max_t = float(filters.get("max_transfer_usd", float("inf")))

        events_result = await db.execute(
            select(Event).where(
                Event.event_type == EventType.transfer,
                or_(Event.actor_id.in_(person_ids), Event.target_id.in_(person_ids)),
            )
        )
        transfer_events = events_result.scalars().all()

        qualifying_person_ids: set[str] = set()
        for e in transfer_events:
            amount = float((e.metadata_ or {}).get("amount_usd", 0))
            if min_t <= amount <= max_t:
                qualifying_person_ids.add(e.actor_id)
                qualifying_person_ids.add(e.target_id)

        persons = [p for p in persons if p.id in qualifying_person_ids]

    return NLSearchResponse(
        persons=list(persons),
        total=len(persons),
        query=body.query,
        filters_applied=filters,
    )
