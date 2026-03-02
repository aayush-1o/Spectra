# SimSight — Session Handoff Document

> Fill this out at the end of every work session so the next session can pick up exactly where you left off.

---

## Current Phase

**Phase**: 3 — Graph Relationships + Anomaly Detection

---

## Phase Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Architecture + Repo Setup | ✅ Complete |
| 1 | Core Setup (DB, Auth, Data Gen skeleton) | ✅ Complete |
| 2 | Synthetic Data Engine | ✅ Complete |
| 3 | Graph Relationships + Anomaly Detection | ✅ Complete |
| 4 | Frontend + Backend Integration | ✅ Complete |
| 5 | Optimisation | 🔲 Not Started |
| 6 | Testing + Hardening | 🔲 Not Started |
| 7 | Deployment | 🔲 Not Started |
| 8 | Documentation + Mastery | 🔲 Not Started |

> Status key: 🔲 Not Started | 🔄 In Progress | ✅ Complete | 🚧 Blocked

---

## What Has Been Built

### Phase 0 — Architecture
- [x] `docs/ARCHITECTURE.md`, `docs/FOLDER_STRUCTURE.md`, `docs/GIT_BRANCH_STRATEGY.md`, `docs/DEFINITION_OF_DONE.md`

### Phase 1 — Core Infrastructure
- [x] `docker-compose.yml` — postgres + redis + backend
- [x] `backend/app/main.py` — FastAPI with middleware
- [x] `backend/app/models/` — Person, Location, Event, AnomalyRecord, User
- [x] `backend/app/services/auth_service.py` — JWT + bcrypt
- [x] `backend/app/api/v1/auth.py`, `deps.py`
- [x] `backend/app/middleware/ethics_guard.py`
- [x] `backend/alembic/versions/0001_initial_schema.py`

### Phase 2 — Synthetic Data Engine
- [x] `backend/app/data_gen/` — person_generator, location_generator, event_generator, run.py, constants.py
- [x] `backend/app/schemas/` — PersonResponse, LocationResponse, EventResponse
- [x] `backend/app/api/v1/` — persons.py, locations.py, events.py
- [x] `backend/tests/unit/` — test_person_generator, test_event_generator (18 tests pass)

### Phase 3 — Graph + Anomaly Detection
- [x] `docker-compose.yml` — added `spectra-neo4j` (neo4j:5), neo4j env vars in backend, healthcheck, neo4j_data volume
- [x] `backend/requirements.txt` — added `neo4j==5.27.0`
- [x] `backend/app/db/neo4j.py` — async driver singleton, `get_neo4j_driver()`, `close_neo4j_driver()`, `get_neo4j_session()` FastAPI dep
- [x] `backend/app/data_gen/graph_builder.py` — reads Postgres → writes CONTACTED/TRANSACTED/VISITED edges to Neo4j via MERGE
- [x] `backend/app/services/graph_service.py` — `GraphService`: neighbourhood, centrality, shortest_path
- [x] `backend/app/services/anomaly_service.py` — IsolationForest + z-score + Redis cache (5 min TTL)
- [x] `backend/app/schemas/graph.py` — GraphNode, GraphEdge, NeighbourhoodResponse, CentralityEntry, PathResponse
- [x] `backend/app/schemas/anomaly.py` — AnomalyResponse, DetectionResult
- [x] `backend/app/api/v1/graph.py` — neighbourhood, centrality, shortest-path endpoints
- [x] `backend/app/api/v1/anomalies.py` — list anomalies, get by id, run-detection
- [x] `backend/app/main.py` — lifespan context + 2 new routers wired
- [x] `backend/app/config.py` — neo4j_password default updated to `spectra123`
- [x] `backend/tests/unit/test_anomaly_service.py` — 4 unit tests
- [x] `backend/tests/integration/test_graph_api.py` — 4 integration tests (auth enforcement)

---

## What Is Pending

### Phase 4 Deliverables — Frontend + Backend Integration
- [ ] Dashboard page wired to real API data (persons, events counts)
- [ ] Graph visualisation component (D3.js or Sigma.js) using `/api/v1/graph/neighbourhood`
- [ ] Anomaly list component using `/api/v1/anomalies`
- [ ] Authentication flow: login/register UI connected to `/api/v1/auth`
- [ ] Pagination controls on persons/events/anomalies tables
- [ ] Vite proxy already configured for `/api` → `http://localhost:8000`

---

## Known Bugs / Gotchas

| # | Description | Area | Severity |
|---|-------------|------|----------|
| 1 | Neo4j healthcheck uses `wget` — image must have it (neo4j:5 does) | docker-compose | Low |
| 2 | `get_async_session()` is an async generator; `graph_builder.py` uses `async for … break` pattern | graph_builder | Low |
| 3 | IDE shows "Cannot find import" for all packages — Pyre2 doesn't see Docker's site-packages | All files | Info |
| 4 | `run_detection` does not deduplicate across multiple runs (same event can be flagged again) | anomaly_service | Medium |

### Phase 3 Design Decisions
- **Async Neo4j driver** (`AsyncGraphDatabase`) used throughout — no sync blocking calls
- **MERGE** (not CREATE) in graph_builder — idempotent, safe to re-run
- **IsolationForest** uses `contamination=0.05` (flags ~5% of events as anomalies)
- **Z-score threshold** of 2.5σ for high-value transfer detection
- **Redis caching**: 5-minute TTL on `anomaly:last_run` key — repeated API calls return cached summary
- **`AnomalyRecord` model** uses `description` + `anomaly_type` fields (not `reason` as in architecture doc)

---

## How To Run Phase 3

```bash
# 1. Full rebuild (includes Neo4j)
docker compose up --build -d

# 2. Run migrations
docker exec spectra-backend alembic upgrade head

# 3. Seed synthetic data (if not already done)
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# 4. Build graph layer in Neo4j
docker exec spectra-backend python -m app.data_gen.graph_builder

# 5. Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo2","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 6. Get a person ID
PERSON_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/persons?limit=1" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# 7. Query the graph
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/graph/neighbourhood/$PERSON_ID?hops=2"

# 8. Run anomaly detection
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/anomalies/run-detection

# 9. List anomalies
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/anomalies?limit=5"

# 10. Run all tests
docker exec spectra-backend pytest tests/unit/ tests/integration/ -v
```

---

*Update this file before ending every session.*
