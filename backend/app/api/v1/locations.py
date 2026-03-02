"""
Spectra — Locations API (v1)
GET /api/v1/locations — paginated list of synthetic locations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.location import Location
from app.models.user import User
from app.schemas.location import LocationResponse

router = APIRouter()

_MAX_LIMIT = 100


@router.get("", response_model=list[LocationResponse])
async def list_locations(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LocationResponse]:
    """Return a paginated list of synthetic locations.  Requires Bearer JWT."""
    if limit > _MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"limit must be ≤ {_MAX_LIMIT}",
        )

    stmt = select(Location).offset(offset).limit(limit).order_by(Location.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()
