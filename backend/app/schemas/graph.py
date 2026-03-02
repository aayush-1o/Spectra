"""
Spectra — Graph Pydantic Schemas
"""

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    properties: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    properties: dict = {}


class NeighbourhoodResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class CentralityEntry(BaseModel):
    person_id: str
    fake_name: str | None = None
    degree: int


class PathResponse(BaseModel):
    path: list[str]  # ordered person IDs
