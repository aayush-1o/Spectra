# SimSight — Session Handoff Document

> Fill this out at the end of every work session so the next session can pick up exactly where you left off.

---

## Current Phase

**Phase**: 8 — AI + Risk Intelligence Layer ✅ **COMPLETE**

---

## Phase Status

| Phase | Name | Status |
|-------|------|---------|
| 0 | Architecture + Repo Setup | ✅ Complete |
| 1 | Core Setup (DB, Auth, Data Gen skeleton) | ✅ Complete |
| 2 | Synthetic Data Engine | ✅ Complete |
| 3 | Graph Relationships + Anomaly Detection | ✅ Complete |
| 4 | Frontend + Backend Integration | ✅ Complete |
| 5 | Optimisation | ✅ Complete |
| 6 | Testing + Hardening | ✅ Complete |
| 7 | Deployment | ✅ Complete |
| **8** | **AI + Risk Intelligence Layer** | ✅ **Complete** |

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
- [x] `docker-compose.yml` — added `spectra-neo4j` (neo4j:5)
- [x] `backend/app/db/neo4j.py` — async driver singleton
- [x] `backend/app/data_gen/graph_builder.py` — Postgres → Neo4j graph
- [x] `backend/app/services/graph_service.py` — neighbourhood, centrality, shortest_path
- [x] `backend/app/services/anomaly_service.py` — IsolationForest + z-score
- [x] `backend/app/api/v1/graph.py`, `anomalies.py`
- [x] `backend/tests/unit/test_anomaly_service.py`, `tests/integration/test_graph_api.py`

### Phase 4 — Frontend + Backend Integration
- [x] React 18 + Vite SPA with 8 pages (Dashboard, Map, Graph, Anomalies, Search, Login, Register, About)
- [x] Axios API client with JWT interceptors
- [x] Protected/public route guards
- [x] Cytoscape.js graph viewer, Leaflet.js map
- [x] `frontend/src/tests/` — component + page tests with Vitest

### Phase 5 — Optimisation
- [x] GIN trigram index, anomaly unique constraint, Redis connection pool
- [x] `TimingMiddleware`, `GET /api/v1/admin/metrics`
- [x] Multi-stage Dockerfiles, React.lazy code-splitting

### Phase 6 — Testing + Hardening
- [x] Completed prior to Phase 7

### Phase 7 — Deployment
- [x] `backend/app/config.py` — production flags + `validate_production()`
- [x] `/health` + `/ready` deep probe endpoints
- [x] `StructuredLoggingMiddleware`, CI/CD workflows, `render.yaml`, `vercel.json`
- [x] `docs/DEPLOYMENT.md`, `docs/PHASE-7-EXPLANATION.md`

---

### Phase 8 — AI + Risk Intelligence Layer ✅

#### 8.1 Richer Synthetic Data
- [x] `backend/app/data_gen/constants.py` — SYNTHETIC_ORGS, NATIONALITIES, RISK_CATEGORIES, FAKE_PLATFORMS, DISTRICTS, THREAT_LEVELS, CALL_CHANNELS, TRANSFER_CURRENCIES, FAKE_ALIASES
- [x] `backend/app/data_gen/person_generator.py` — fake_phone_primary/secondary, fake_email, fake_nationality, fake_alias, risk_category, group_memberships, fake_id_number
- [x] `backend/app/data_gen/event_generator.py` — channel/is_encrypted (call), content_hash/platform (message), currency/recipient_account (transfer), attendee_count/is_covert (meeting)
- [x] `backend/app/data_gen/location_generator.py` — district, threat_level (weighted), surveillance_coverage
- [x] `backend/app/models/person.py` — 12 new columns (contact info, risk_score, aliases, group_memberships)
- [x] `backend/app/models/location.py` — 3 new columns (district, threat_level, surveillance_coverage)
- [x] `backend/alembic/versions/0004_richer_persons.py` — ADD COLUMN migration (15 columns)
- [x] `backend/app/schemas/person.py` — PersonResponse updated
- [x] `backend/app/schemas/location.py` — LocationResponse updated
- [x] `frontend/src/types/index.ts` — Person + Location TypeScript interfaces updated

#### 8.2 Person Risk Score
- [x] `backend/app/services/risk_service.py` — `compute_risk_score()` (4-factor formula) + `compute_all_risk_scores()` (batch)
- [x] `backend/app/api/v1/admin.py` — `POST /api/v1/admin/compute-risk-scores`

#### 8.3 RiskBadge Component
- [x] `frontend/src/components/shared/RiskBadge.tsx` — 4-tier color badge (low/medium/high/critical)

#### 8.4 Person Detail Page
- [x] `frontend/src/pages/PersonDetailPage.tsx` — full profile, identity/contact/affiliations cards
- [x] Route `/person/:id` added to `frontend/src/App.tsx`

#### 8.5 Entity Timeline
- [x] `frontend/src/components/timeline/EntityTimeline.tsx` — vertical chronological event history
- [x] `backend/app/api/v1/events.py` — added `?person_id=` filter

#### 8.6 NL Search Backend
- [x] `backend/app/services/nl_search_service.py` — Claude-powered query-to-filters
- [x] `backend/app/api/v1/search.py` — `POST /api/v1/search/nl`
- [x] `backend/app/main.py` — search router registered

#### 8.7 AI Summary
- [x] `backend/app/services/ai_summary_service.py` — Claude analyst report generator
- [x] `backend/app/api/v1/persons.py` — `GET /{id}` (single person) + `GET /{id}/summary` (AI report)
- [x] `frontend/src/components/person/AISummaryPanel.tsx` — document-styled Claude report viewer

#### 8.8 NL Search Frontend
- [x] `frontend/src/components/shared/NLSearchBar.tsx` — ✨ NL search bar with result cards
- [x] `frontend/src/pages/SearchPage.tsx` — Name / AI Search tab toggle

#### 8.9 Map Heatmap
- [x] `leaflet.heat` installed (`npm install leaflet.heat`)
- [x] `frontend/src/pages/MapPage.tsx` — Pins/Heatmap toggle; heatmap intensity = event count per location

#### 8.10 Graph Community + Risk Coloring
- [x] `backend/app/services/community_service.py` — Louvain detection + networkx fallback, Redis cache 600s
- [x] `backend/app/api/v1/graph.py` — `GET /api/v1/graph/communities`
- [x] `backend/app/data_gen/graph_builder.py` — writes `risk_score` + `risk_category` to Neo4j Person nodes
- [x] `frontend/src/components/graph/CytoscapeGraph.tsx` — Risk mode (green→red) + Community mode (12-colour palette), toggle + legend

#### 8.11 Richer Anomaly Detection
- [x] `backend/app/services/anomaly_service.py` — DBSCAN, LOF, Night Owl Rule (>60% night events)
- [x] `backend/app/models/anomaly.py` — `dbscan`, `lof`, `night_owl_rule` added to AnomalyAlgorithm enum
- [x] `backend/alembic/versions/0005_anomaly_algorithms.py` — `ALTER TYPE … ADD VALUE IF NOT EXISTS`

#### 8.12 Tests
- [x] `backend/tests/test_phase8.py` — 14 unit tests (risk score 6, NL search 4, AnomalyAlgorithm 4)

#### Config + Dependencies
- [x] `backend/app/config.py` — `ANTHROPIC_API_KEY` + `GOOGLE_API_KEY` settings, NEO4J_PASSWORD production guard
- [x] `backend/requirements.txt` — `anthropic==0.40.0`, `python-louvain==0.16`
- [x] `.env.example` — `ANTHROPIC_API_KEY` + `GOOGLE_API_KEY` documented

#### Documentation
- [x] `README.md` — Phase 8 badge, feature table, API table, quick-start updated
- [x] `docs/HANDOFF.md` — Phase 8 section added (this file)
- [x] `docs/PHASE-8-EXPLANATION.md` — deep-dive explanation

---

## Environment Variables Required

| Variable | Required | Where Used |
|----------|----------|-----------|
| `DATABASE_URL` | ✅ Always | Postgres connection |
| `NEO4J_URI` | ✅ Always | Neo4j connection |
| `NEO4J_USERNAME` | ✅ Always | Neo4j auth |
| `NEO4J_PASSWORD` | ✅ Always | Neo4j auth |
| `REDIS_URL` | ✅ Always | Redis connection |
| `JWT_SECRET_KEY` | ✅ Always | Auth tokens |
| `ANTHROPIC_API_KEY` | ⚡ AI features | NL Search + AI Summary |
| `GOOGLE_API_KEY` | ⚡ Optional | Maps / Gemini AI |
| `VITE_API_BASE_URL` | ✅ Frontend | API base URL |

---

## Deployment URLs (update once live)

| Service | URL |
|---------|-----|
| Backend API | https://spectra-api.onrender.com |
| Frontend | https://spectra-simsight.vercel.app |
| Health | https://spectra-api.onrender.com/health |
| Ready | https://spectra-api.onrender.com/ready |

## Production Services

| Service | Platform | Notes |
|---------|----------|-------|
| Backend | Render (free) | Docker deploy, auto-migrate on start |
| Frontend | Vercel (free) | CDN + HTTPS |
| PostgreSQL | Render Postgres (free) | 1GB, 90-day expiry on free tier |
| Redis | Upstash (free) | 10k cmd/day, TLS (`rediss://`) |
| Neo4j | AuraDB Free | 200MB, always-on |

---

## How To Run Phase 8 (Fresh Start)

```bash
# 1. Full rebuild
docker compose up --build -d

# 2. Run all migrations (0001 → 0005)
docker exec spectra-backend alembic upgrade head

# 3. Generate Phase 8 synthetic data
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# 4. Build Neo4j graph (writes risk_score to Person nodes)
docker exec spectra-backend python -m app.data_gen.graph_builder

# 5. Compute initial risk scores
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/compute-risk-scores

# 6. Run Phase 8 tests
docker exec spectra-backend pytest tests/test_phase8.py -v

# 7. Test AI features (requires ANTHROPIC_API_KEY in .env)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "people with high risk scores who made large transfers"}' \
  http://localhost:8000/api/v1/search/nl
```

---

## Known Nuances + Design Decisions

| # | Description | Area | Severity |
|---|-------------|------|----------|
| 1 | Pyre2 shows "Cannot find import" for all `app.*` — it doesn't have Docker's Python path. Safe to ignore. | All files | Info |
| 2 | `transfer_amount` filtering in NL search is done Python-side (not SQL) because `metadata_` is JSONB. Max 50 results. | `search.py` | Low |
| 3 | Louvain community detection uses `random_state=42` for reproducibility, but results are cached 600s anyway. | `community_service.py` | Low |
| 4 | `graph_builder.py` uses `async for … break` pattern to get a single session from the async generator. | `graph_builder.py` | Low |
| 5 | `ANTHROPIC_API_KEY` absent → graceful degradation: NL search returns empty filters, AI summary returns a placeholder string. No crash. | AI services | Info |
| 6 | Night Owl Rule anomaly records are person-level (entity_type = "person"), not event-level. | `anomaly_service.py` | Low |

---

*Update this file before ending every session.*
