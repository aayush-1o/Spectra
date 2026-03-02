# Phase 3 — Graph Relationships + Anomaly Detection: Full Explanation

> **Project**: Spectra (SimSight)  ⚠️ SYNTHETIC DATA ONLY.

---

## 1. What Each File Does

| File | Purpose |
|------|---------|
| `app/db/neo4j.py` | Async Neo4j driver singleton; `get_neo4j_session()` FastAPI dependency |
| `app/data_gen/graph_builder.py` | CLI: reads Postgres events → writes edges to Neo4j via MERGE |
| `app/services/graph_service.py` | `GraphService`: neighbourhood, centrality, shortest-path Cypher queries |
| `app/services/anomaly_service.py` | IsolationForest + z-score detection; Redis caching; Postgres persistence |
| `app/schemas/graph.py` | Response schemas: GraphNode, GraphEdge, NeighbourhoodResponse, etc. |
| `app/schemas/anomaly.py` | AnomalyResponse, DetectionResult |
| `app/api/v1/graph.py` | Three graph API endpoints (all auth-protected) |
| `app/api/v1/anomalies.py` | Three anomaly API endpoints + Redis dependency |

---

## 2. How Neo4j Edges Are Built From Postgres Events

```
Postgres Events table
      │
      ▼
graph_builder.py loads all rows via async SQLAlchemy
      │
      ├─ call/message events → MERGE (:Person)-[:CONTACTED]->(:Person)
      ├─ transfer events     → MERGE (:Person)-[:TRANSACTED {amount_usd}]->(:Person)
      └─ meeting events      → MERGE (:Person)-[:VISITED]->(:Location)
```

**Why MERGE instead of CREATE?**  
`MERGE` is idempotent — re-running `graph_builder.py` won't duplicate edges. It matches on the `event_id` property, so each Postgres event maps to exactly one Neo4j relationship.

**Batching**: All events of the same type are batched into a single `UNWIND $events AS e ... MERGE` query. This is far more efficient than one Cypher per event.

---

## 3. How IsolationForest Anomaly Detection Works

**IsolationForest** is an unsupervised ML algorithm that identifies outliers by how easily a data point can be "isolated" using random splits.

**Feature matrix** (3 features per event):
```
[ hour_of_day (0–23),  amount_usd (0–50000),  duration_seconds (0–3600) ]
```

**Steps**:
1. Build feature matrix `X` from all events.
2. Fit `IsolationForest(contamination=0.05, n_estimators=100)` — flags the 5% most anomalous points.
3. `fit_predict(X)` returns `-1` for outliers, `+1` for normal.
4. `decision_function(X)` returns raw anomaly scores (more negative = more anomalous).
5. Normalise score to `[0, 1]` for storage.
6. Persist as `AnomalyRecord(algorithm=isolation_forest)` rows.

**Z-score** supplements IF for transfer amounts:
- Mean and std dev of all transfer `amount_usd` values are computed.
- Events with `|z| > 2.5` (2.5 standard deviations above mean) are flagged as `high_value_transfer`.

---

## 4. How Redis Caching Is Implemented

```python
await redis_client.set("anomaly:last_run", json.dumps(summary), ex=300)
```

- **Key**: `anomaly:last_run`
- **Value**: `{"flagged": N, "duration_ms": N}` as JSON string
- **TTL**: 300 seconds (5 minutes)
- **Failure mode**: Redis failure is silently ignored (`try/except`) — detection result is returned regardless.
- **Consumer**: The `run-detection` endpoint saves to Redis. A future read endpoint could serve the cached summary without re-running detection.

---

## 5. How the Async Neo4j Driver Works

```python
# Module-level singleton
_driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))

# Session per request
async with driver.session(database="neo4j") as session:
    result = await session.run("MATCH (p:Person) RETURN p LIMIT 10")
    records = await result.data()
```

- `AsyncGraphDatabase.driver()` creates a connection pool automatically.
- Sessions are lightweight — one per request, closed automatically via `async with`.
- The driver is closed on FastAPI shutdown via the `lifespan` context manager in `main.py`.

---

## 6. Step-by-Step Guide to Run Phase 3

```bash
# 1. Rebuild with Neo4j
docker compose up --build -d

# 2. Wait ~30s for Neo4j to initialise, then verify health
docker ps  # spectra-neo4j should show "(healthy)"

# 3. Apply migrations
docker exec spectra-backend alembic upgrade head

# 4. Generate synthetic data (if needed)
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# 5. Build the graph
docker exec spectra-backend python -m app.data_gen.graph_builder

# 6. Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo2","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 7. Get a person ID to query
PERSON_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/persons?limit=1" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# 8. Query neighbourhood graph (2 hops)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/graph/neighbourhood/$PERSON_ID?hops=2"

# 9. Get top-20 central nodes
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/graph/centrality?top_n=5"

# 10. Run anomaly detection
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/anomalies/run-detection | python3 -m json.tool

# 11. List anomalies
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/anomalies?limit=5" | python3 -m json.tool

# 12. Run all tests
docker exec spectra-backend pytest tests/unit/ tests/integration/ -v
```

---

## 7. Common Bugs and Fixes

### `neo4j.exceptions.ServiceUnavailable`
**Cause**: Neo4j not yet fully started when graph_builder runs.  
**Fix**: Wait for `spectra-neo4j` to show `(healthy)` in `docker ps`. Takes ~30s on first launch.

### `AuthError: UNAUTHENTICATED`
**Cause**: Wrong password in Neo4j bolt connection. Container uses `NEO4J_AUTH=neo4j/spectra123`.  
**Fix**: Ensure `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` env vars in docker-compose match `config.py` defaults.

### `graph_builder.py` produces 0 edges
**Cause**: No event data in Postgres yet.  
**Fix**: Run `python -m app.data_gen.run` first, then `graph_builder.py`.

### `run-detection` returns `{"flagged": 0}`
**Cause**: Fewer than 10 events (IsolationForest minimum) or events all look normal.  
**Fix**: Run with `--events 800` (default). IsolationForest needs at least 10 samples.

### `ModuleNotFoundError: No module named 'neo4j'`
**Cause**: Docker image not rebuilt after adding `neo4j==5.27.0` to requirements.txt.  
**Fix**: `docker compose up --build -d` (forces pip install).

---

## 8. Manual Debugging — Cypher Queries + Redis Inspection

### Neo4j Browser
Open `http://localhost:7474` → login: `neo4j` / `spectra123`

```cypher
-- Count all nodes by label
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count;

-- Sample 5 person nodes
MATCH (p:Person) RETURN p LIMIT 5;

-- Count relationships by type
MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY count(r) DESC;

-- 2-hop neighbourhood of a specific person
MATCH path = (start:Person {id: "PASTE-PERSON-ID-HERE"})-[*1..2]-(other)
RETURN path LIMIT 50;

-- Shortest path between two persons
MATCH (a:Person {id: "ID1"}), (b:Person {id: "ID2"}),
      path = shortestPath((a)-[*]-(b))
RETURN [n in nodes(path) | n.id] AS path;

-- Top-10 most connected nodes
MATCH (p:Person)
OPTIONAL MATCH (p)-[r]-()
WITH p, count(r) AS degree
ORDER BY degree DESC LIMIT 10
RETURN p.id, p.fake_name, degree;
```

### Redis Inspection
```bash
docker exec spectra-redis redis-cli

# Check if anomaly detection result is cached
GET anomaly:last_run

# Check TTL remaining
TTL anomaly:last_run

# Clear cache (forces re-detection next run)
DEL anomaly:last_run
```

---

## 9. Interview Questions You Should Be Able to Answer

**Q: What is IsolationForest and why use it for anomaly detection?**  
A: IsolationForest identifies outliers by measuring how few random splits it takes to isolate a point. Anomalies are isolated quickly (fewer splits) because they're rare and extreme. We use it because it's unsupervised (no labelled training data needed), scales well, and works on tabular numeric features.

**Q: Why MERGE instead of CREATE in Neo4j?**  
A: `MERGE` is idempotent — it matches existing nodes/relationships and only creates them if they don't exist. `CREATE` would add duplicates on every re-run. Our unique key is `event_id` on the relationship, mapping each Postgres event to exactly one Neo4j edge.

**Q: What is degree centrality and how is it computed in your Cypher query?**  
A: Degree centrality = total number of relationships a node participates in. In the Cypher query: `MATCH (p:Person) OPTIONAL MATCH (p)-[r]-() WITH p, count(r) AS degree`. This counts both incoming and outgoing relationships of any type.

**Q: Why is the Neo4j driver a module-level singleton?**  
A: Creating a driver is expensive (establishes a connection pool). Sharing one instance across all requests avoids the overhead of opening/closing connections per request. The singleton is closed gracefully in the FastAPI `lifespan` shutdown hook.

**Q: What happens if Redis goes down during anomaly detection?**  
A: The detection still runs and the results are saved to Postgres. The Redis write is wrapped in `try/except` and failure is silently ignored. The cost is that the next `run-detection` call won't be able to return a cached result — it will re-run detection.

**Q: How does the variable-hop neighbourhood query work in Cypher?**  
A: `MATCH path = (start:Person {id: $id})-[*1..N]-(other)` uses variable-length path matching. The `*1..N` syntax means "between 1 and N hops, following any relationship type, in either direction". We clamp N to max 5 to prevent runaway queries on densely connected graphs.
