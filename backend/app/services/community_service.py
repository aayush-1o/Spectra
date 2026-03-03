"""
Spectra — Community Detection Service
Reads Neo4j edges into networkx, runs Louvain community detection,
caches results in Redis (TTL 600s).

Requirements: python-louvain (package: community), networkx

⚠️ All graph data is synthetic. Community assignments have no real-world meaning.
"""

import json
import logging

import networkx as nx
import redis.asyncio as aioredis

from app.db.redis import CacheHelper

logger = logging.getLogger(__name__)

_REDIS_KEY = "graph:communities"
_REDIS_TTL = 600  # 10 minutes


async def detect_communities(
    neo4j_session,
    redis_client: aioredis.Redis,
) -> dict:
    """
    Run Louvain community detection on the Neo4j graph.

    Steps:
      1. Load all person–person edges from Neo4j.
      2. Build an undirected networkx graph.
      3. Run Louvain community detection.
      4. Cache result in Redis with TTL 600s.

    Returns:
        {
            "communities": {person_id: community_id, ...},
            "community_count": int,
        }
    """
    # ── Check Redis cache first ───────────────────────────────────────────────
    cached = await CacheHelper.get(redis_client, _REDIS_KEY)
    if cached:
        logger.debug("Community cache HIT")
        return json.loads(cached)

    logger.debug("Community cache MISS — running Louvain detection")

    # ── Load edges from Neo4j ─────────────────────────────────────────────────
    result = await neo4j_session.run(
        """
        MATCH (a:Person)-[r:CONTACTED|TRANSACTED|VISITED]->(b:Person)
        RETURN a.id AS source, b.id AS target
        LIMIT 10000
        """
    )
    records = await result.data()

    G = nx.Graph()
    for rec in records:
        src = rec.get("source")
        tgt = rec.get("target")
        if src and tgt:
            G.add_edge(src, tgt)

    if G.number_of_nodes() == 0:
        return {"communities": {}, "community_count": 0}

    # ── Run Louvain community detection ───────────────────────────────────────
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G, random_state=42)
    except ImportError:
        # Fallback: use networkx greedy modularity communities
        logger.warning("python-louvain not installed, using networkx greedy_modularity_communities fallback")
        communities_iter = nx.community.greedy_modularity_communities(G)
        partition = {}
        for community_id, nodes in enumerate(communities_iter):
            for node in nodes:
                partition[node] = community_id

    community_count = len(set(partition.values()))
    data = {
        "communities": partition,
        "community_count": community_count,
    }

    # ── Cache result ──────────────────────────────────────────────────────────
    try:
        await CacheHelper.set(redis_client, _REDIS_KEY, json.dumps(data), _REDIS_TTL)
    except Exception as e:
        logger.warning("Failed to cache communities: %s", e)

    logger.info("Louvain: %d nodes → %d communities", G.number_of_nodes(), community_count)
    return data
