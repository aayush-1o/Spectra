# SimSight — Session Handoff Document

> Fill this out at the end of every work session so the next session can pick up exactly where you left off.

---

## Current Phase

**Phase**: 7 — Deployment ✅

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
| 7 | Deployment | ✅ **Complete** |
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

### Phase 5 — Optimisation ✅
- [x] `backend/alembic/versions/0003_performance_indexes.py` — GIN trigram index + anomaly unique constraint
- [x] `backend/app/services/anomaly_service.py` — full deduplication + `get_anomaly_count()`
- [x] `backend/app/db/neo4j.py` — `ensure_neo4j_indexes()` called on startup
- [x] `backend/app/db/redis.py` — shared connection pool (20 conns) + `CacheHelper` with hit/miss stats
- [x] `backend/app/middleware/timing.py` — `TimingMiddleware` (slow log, rolling avg, `X-Response-Time-Ms`)
- [x] `backend/app/api/v1/admin.py` — `GET /api/v1/admin/metrics` endpoint
- [x] `backend/app/api/v1/graph.py` — neighbourhood Redis cache (TTL 120s)
- [x] `backend/app/api/v1/anomalies.py` — uses shared Redis pool
- [x] `backend/app/main.py` — lifespan wires all new components, middleware order fixed
- [x] `backend/Dockerfile` — multi-stage (builder + slim runtime)
- [x] `backend/.dockerignore` — excludes tests, caches, migrations from image
- [x] `frontend/Dockerfile` — multi-stage (Node build + nginx:alpine serve)
- [x] `frontend/nginx.conf` — React Router fallback + static asset caching + API proxy
- [x] `frontend/.dockerignore` — excludes node_modules/dist
- [x] `docker-compose.yml` — `spectra-frontend` service, Redis persistence volume
- [x] `frontend/src/App.tsx` — lazy-loaded heavy pages via React.lazy + Suspense
- [x] `frontend/src/hooks/useDebounce.ts` — 300ms debounce for search inputs
- [x] `frontend/src/utils/perf.ts` — `measureAsync` / `measureSync` / `markRender`
- [x] `backend/requirements.txt` — added `pytest-benchmark==4.0.0`
- [x] `backend/tests/unit/test_performance.py` — feature matrix speed + dedup logic
- [x] `backend/tests/unit/test_redis_fallback.py` — CacheHelper graceful degradation
- [x] `backend/tests/unit/test_indexes.py` — static migration analysis
- [x] `backend/tests/unit/test_timing_middleware.py` — header, log, deque tests
### Phase 6 — Testing + Hardening
- [x] Phase 6 (Testing + Hardening) — completed prior to Phase 7

### Phase 7 — Deployment ✅
- [x] `backend/app/config.py` — Phase 7 config flags: `LOG_LEVEL`, `DEBUG`, `ALLOW_DOCS`, `FRONTEND_URL`, `CORS_ORIGINS_OVERRIDE`, `validate_production()` startup guard
- [x] `backend/app/main.py` — deep `/health` + `/ready` endpoints (ping all 3 services), `StructuredLoggingMiddleware`, `/docs` disabled in production, version 0.7.0
- [x] `backend/app/db/postgres.py` — DATABASE_URL rewrite (`postgresql://` → `postgresql+asyncpg://`) for Render compatibility
- [x] `backend/app/middleware/logging.py` — `StructuredLoggingMiddleware`: JSON in production, human-readable in dev, DEBUG for health probes, ERROR for 5xx
- [x] `backend/scripts/migrate_and_start.sh` — runs `alembic upgrade head` then starts uvicorn (2 workers, respects `$PORT`)
- [x] `backend/.env.production.example` — cloud-ready env var template (Render/Upstash/AuraDB formats)
- [x] `.env.example` — updated with all Phase 7 vars + cloud format comments
- [x] `.github/workflows/ci.yml` — CI on PR to dev/main: backend tests (Postgres + Redis service containers), frontend tests, ruff + eslint lint
- [x] `.github/workflows/deploy.yml` — Deploy on push to main: pre-deploy tests, Render deploy hook, Vercel CLI prod deploy
- [x] `render.yaml` — Render Blueprint: web service + managed Postgres, env vars, health check path, auto-deploy
- [x] `vercel.json` — SPA rewrite rules, security headers, immutable asset caching
- [x] `docker-compose.prod.yml` — production overrides: no local DBs, migrate-and-start command, ENVIRONMENT=production
- [x] `docs/DEPLOYMENT.md` — step-by-step guide: AuraDB, Upstash, Render, Vercel, GitHub Actions secrets, migration, JWT rotation, log inspection, rollback
- [x] `docs/PHASE-7-EXPLANATION.md` — infra architecture diagram, platform choices, env separation, CI/CD flow, health/ready explanation, JSON log format, security checklist, production risks, rollback strategy

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

## GitHub Actions Secrets Required

| Secret | Used By |
|--------|---------|
| `RENDER_DEPLOY_HOOK_URL` | `deploy.yml` — triggers Render re-deploy |
| `VERCEL_TOKEN` | `deploy.yml` — authenticates Vercel CLI |
| `VERCEL_ORG_ID` | `deploy.yml` — Vercel project org |
| `VERCEL_PROJECT_ID` | `deploy.yml` — Vercel project ID |


| # | Description | Area | Severity |
|---|-------------|------|----------|
| 1 | Neo4j healthcheck uses `wget` — image must have it (neo4j:5 does) | docker-compose | Low |
| 2 | `get_async_session()` is an async generator; `graph_builder.py` uses `async for … break` pattern | graph_builder | Low |
| 3 | IDE shows "Cannot find import" for all packages — Pyre2 doesn't see Docker's site-packages | All files | Info |
| 4 | `CONCURRENTLY` in migration 0003 requires no active DB transaction — Alembic runs each migration in its own transaction so this is safe | migration | Low |
| 5 | TimingMiddleware rolling deque is in-process memory — resets on container restart | timing.py | Low |
| 6 | Frontend `spectra-frontend` Docker service is production-only (nginx); local dev still uses `npm run dev` on port 5173 | frontend | Info |

---

## Phase 5 Design Decisions

- **Middleware order**: CORS (outermost) → TimingMiddleware → EthicsGuard (innermost). CORS is outermost so preflight OPTIONS skip timing and ethics checks.
- **GIN trigram**: Enables `ILIKE '%term%'` without a sequential scan. Requires `pg_trgm` extension.
- **Dedup strategy**: DB-level unique index + in-service pre-check. The pre-check avoids constraint errors on concurrent runs; the index is the definitive guard.
- **Redis pool size**: 20 connections — generous for <100 concurrent users, conservative for free-tier Redis.
- **Lazy loading strategy**: Auth pages (Login, Register) stay eager — they're tiny and always the first screen. Everything else is split.

---

## How To Run Phase 5

```bash
# 1. Full rebuild (picks up multi-stage Dockerfile changes)
docker compose up --build -d

# 2. Run all migrations (including Phase 5 performance indexes)
docker exec spectra-backend alembic upgrade head

# 3. Verify Phase 5 tests pass
docker exec spectra-backend pytest tests/unit/test_performance.py \
  tests/unit/test_redis_fallback.py \
  tests/unit/test_indexes.py \
  tests/unit/test_timing_middleware.py -v

# 4. Run full test suite
docker exec spectra-backend pytest tests/ -v

# 5. Test metrics endpoint
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo2","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/admin/metrics | python3 -m json.tool

# 6. Verify X-Response-Time-Ms header present
curl -I -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/persons

# 7. Test graph caching (2nd call should be faster)
PERSON_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/persons?limit=1" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
time curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/graph/neighbourhood/$PERSON_ID?hops=2" > /dev/null
time curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/graph/neighbourhood/$PERSON_ID?hops=2" > /dev/null

# 8. Test anomaly deduplication (2nd run returns flagged=0)
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/anomalies/run-detection
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/anomalies/run-detection
```

---

*Update this file before ending every session.*
