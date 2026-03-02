"""
Spectra — Graph API (v1)
Neighbourhood, centrality, and shortest-path queries against Neo4j.
"""

import neo4j
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_current_user
from app.db.neo4j import get_neo4j_session
from app.models.user import User
from app.schemas.graph import CentralityEntry, NeighbourhoodResponse, PathResponse
from app.services.graph_service import GraphService

router = APIRouter()


@router.get("/neighbourhood/{person_id}", response_model=NeighbourhoodResponse)
async def get_neighbourhood(
    person_id: str,
    hops: int = Query(default=2, ge=1, le=5, description="Number of hops from the seed person"),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    _current_user: User = Depends(get_current_user),
) -> NeighbourhoodResponse:
    """Return all nodes and edges within N hops of a given person. Requires Bearer JWT."""
    svc = GraphService(neo4j_session)
    result = await svc.get_neighbourhood(person_id, hops)
    return NeighbourhoodResponse(
        nodes=result["nodes"],
        edges=result["edges"],
    )


@router.get("/centrality", response_model=list[CentralityEntry])
async def get_centrality(
    top_n: int = Query(default=20, ge=1, le=100),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    _current_user: User = Depends(get_current_user),
) -> list[CentralityEntry]:
    """Return top-N persons ranked by degree centrality. Requires Bearer JWT."""
    svc = GraphService(neo4j_session)
    return await svc.get_centrality(top_n)


@router.get("/shortest-path", response_model=PathResponse)
async def get_shortest_path(
    from_id: str = Query(..., description="Source person ID"),
    to_id: str = Query(..., description="Target person ID"),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    _current_user: User = Depends(get_current_user),
) -> PathResponse:
    """Find the shortest path between two persons. Requires Bearer JWT."""
    if from_id == to_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_id and to_id must be different persons.",
        )
    svc = GraphService(neo4j_session)
    path = await svc.get_shortest_path(from_id, to_id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No path found between the two persons.",
        )
    return PathResponse(path=path)
