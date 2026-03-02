"""
Spectra — Anomalies API (v1)
Run and retrieve anomaly detection results.
"""

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.anomaly import AnomalyRecord
from app.models.user import User
from app.schemas.anomaly import AnomalyResponse, DetectionResult
from app.services import anomaly_service
from app.config import settings

router = APIRouter()
_MAX_LIMIT = 100


async def _get_redis():
    """Yield a Redis async client for use as a FastAPI dependency."""
    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@router.get("", response_model=list[AnomalyResponse])
async def list_anomalies(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[AnomalyResponse]:
    """Return a paginated list of anomaly records ordered by score descending. Requires Bearer JWT."""
    if limit > _MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"limit must be ≤ {_MAX_LIMIT}",
        )
    return await anomaly_service.get_anomalies(db, limit=limit, offset=offset)


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(
    anomaly_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AnomalyResponse:
    """Return a single anomaly record by ID. Requires Bearer JWT."""
    result = await db.execute(select(AnomalyRecord).where(AnomalyRecord.id == anomaly_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anomaly not found.")
    return record


@router.post("/run-detection", response_model=DetectionResult)
async def run_detection(
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(_get_redis),
    _current_user: User = Depends(get_current_user),
) -> DetectionResult:
    """
    Trigger anomaly detection (IsolationForest + z-score).
    Results are cached in Redis for 5 minutes. Requires Bearer JWT.
    """
    result = await anomaly_service.run_detection(db, redis_client)
    return DetectionResult(**result)
