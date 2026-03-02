"""
Spectra — Graph Service
Cypher queries against Neo4j for neighbourhood, centrality, and shortest-path lookups.
"""

from typing import Any

import neo4j

from app.db.neo4j import get_neo4j_driver


class GraphService:
    """Wraps Neo4j Cypher queries for the graph API."""

    def __init__(self, session: neo4j.AsyncSession):
        self._session = session

    async def get_neighbourhood(self, person_id: str, hops: int = 2) -> dict:
        """
        Return all nodes and edges within `hops` hops of a given Person.
        Returns: {"nodes": [...], "edges": [...]}

        AUDIT FIX: max hops capped at 3 (was 5) and path expansion limited to
        500 paths to prevent supernode explosions on high-degree nodes.
        Returned nodes capped at 200, edges at 300.
        """
        hops = max(1, min(hops, 3))   # clamp 1–3 (was 1–5 — too risky at scale)
        result = await self._session.run(
            f"""
            MATCH path = (start:Person {{id: $id}})-[*1..{hops}]-(other)
            WITH path LIMIT 500
            UNWIND nodes(path) AS n
            UNWIND relationships(path) AS r
            WITH
                collect(DISTINCT {{
                    id: n.id,
                    label: labels(n)[0],
                    properties: {{fake_name: n.fake_name, occupation: n.occupation,
                                  fake_address: n.fake_address, location_type: n.location_type}}
                }})[..200] AS nodes,
                collect(DISTINCT {{
                    source: startNode(r).id,
                    target: endNode(r).id,
                    type: type(r),
                    properties: {{event_id: r.event_id, ts: r.ts, amount_usd: r.amount_usd}}
                }})[..300] AS edges
            RETURN nodes, edges
            """,
            id=person_id,
        )
        record = await result.single()
        if record is None:
            return {"nodes": [], "edges": []}
        return {
            "nodes": [_clean(n) for n in record["nodes"]],
            "edges": [_clean(e) for e in record["edges"]],
        }


    async def get_centrality(self, top_n: int = 20) -> list[dict]:
        """
        Compute degree centrality (total relationship count) for all Person nodes.
        Returns a ranked list: [{"person_id": ..., "degree": ...}]
        """
        result = await self._session.run(
            """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[r]-()
            WITH p, count(r) AS degree
            ORDER BY degree DESC
            LIMIT $top_n
            RETURN p.id AS person_id, p.fake_name AS fake_name, degree
            """,
            top_n=top_n,
        )
        records = await result.data()
        return [{"person_id": r["person_id"], "fake_name": r["fake_name"], "degree": r["degree"]} for r in records]

    async def get_shortest_path(self, from_id: str, to_id: str) -> list[str]:
        """
        Find the shortest path between two Person nodes.
        Returns an ordered list of person IDs (empty if no path exists).
        """
        result = await self._session.run(
            """
            MATCH (a:Person {id: $from_id}), (b:Person {id: $to_id}),
                  path = shortestPath((a)-[*..10]-(b))
            RETURN [n in nodes(path) | n.id] AS path_ids
            """,
            from_id=from_id,
            to_id=to_id,
        )
        record = await result.single()
        if record is None:
            return []
        return record["path_ids"]


def _clean(d: dict) -> dict:
    """Remove None values from a dict to keep API responses clean."""
    return {k: v for k, v in d.items() if v is not None}
