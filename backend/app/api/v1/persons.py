"""
Spectra — Persons API (v1)
GET /api/v1/persons — paginated list of synthetic persons.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonResponse

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
