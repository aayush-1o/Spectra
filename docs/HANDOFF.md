# SimSight — Session Handoff Document

> Fill this out at the end of every work session so the next session (or next AI) can
> pick up exactly where you left off.

---

## Current Phase

<!-- Replace with the active phase number and name -->
**Phase**: 0 — Architecture + Repo Setup

---

## Phase Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Architecture + Repo Setup | ✅ Complete |
| 1 | Core Setup (DB, Auth, Data Gen skeleton) | 🔲 Not Started |
| 2 | Synthetic Data Engine | 🔲 Not Started |
| 3 | Graph Relationships + Anomaly Detection | 🔲 Not Started |
| 4 | Frontend + Backend Integration | 🔲 Not Started |
| 5 | Optimisation | 🔲 Not Started |
| 6 | Testing + Hardening | 🔲 Not Started |
| 7 | Deployment | 🔲 Not Started |
| 8 | Documentation + Mastery | 🔲 Not Started |

> Status key: 🔲 Not Started | 🔄 In Progress | ✅ Complete | 🚧 Blocked

---

## What Has Been Built So Far

<!-- Update this list as features are completed -->
- [x] ARCHITECTURE.md — full system design, tech stack, data model, API list
- [x] HANDOFF.md — this file
- [x] FOLDER_STRUCTURE.md — proposed directory layout
- [x] GIT_BRANCH_STRATEGY.md — branching model
- [x] DEFINITION_OF_DONE.md — per-phase completion criteria
- [ ] Git repo initialised
- [ ] Docker Compose file created
- [ ] PostgreSQL schema + Alembic migrations
- [ ] FastAPI skeleton with health check
- [ ] React + Vite scaffold

---

## What Is Pending

<!-- Paste the next phase's deliverables here -->
### Phase 1 Deliverables
- [ ] `docker-compose.yml` with postgres + redis + backend services
- [ ] FastAPI project scaffold (`backend/`)
- [ ] SQLAlchemy models for Person, Location, Event, AnomalyRecord
- [ ] Alembic migration: initial schema
- [ ] Vite + React scaffold (`frontend/`)
- [ ] JWT auth: `/register`, `/login`, `/me` endpoints
- [ ] `.env.example` with all required variables
- [ ] README with local setup instructions

---

## Known Bugs

| # | Description | File / Area | Severity | Status |
|---|-------------|-------------|----------|--------|
| — | None yet | — | — | — |

---

## Environment Variables Added So Far

```env
# === Backend ===
DATABASE_URL=postgresql+asyncpg://simsight:simsight@localhost:5432/simsight
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=changeme
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=CHANGE_ME_IN_PRODUCTION
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ENVIRONMENT=development  # development | production

# === Frontend (Vite) ===
VITE_API_BASE_URL=http://localhost:8000
```

> ⚠️ Never commit actual secrets. Copy `.env.example` to `.env` and fill in real values locally.

---

## How To Run Locally

> Complete these steps in order every time you start a new session.

### Prerequisites
- Docker Desktop installed and running
- Node.js 20+ and npm installed
- Python 3.11+ installed (for running scripts outside Docker)
- Git configured

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/<your-username>/simsight.git
cd simsight
```

**2. Copy environment variables**
```bash
cp .env.example .env
# Edit .env with any local overrides
```

**3. Start backend services (DB, Redis, API)**
```bash
docker compose up --build
```

**4. Run database migrations** (first time only, or after schema changes)
```bash
docker compose exec backend alembic upgrade head
```

**5. Generate synthetic data** (first time only)
```bash
docker compose exec backend python -m app.data_gen.run --persons 500 --events 2000
```

**6. Start frontend dev server**
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

**7. Verify**
- API health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

---

## Last Commit Hash

```
(fill in before ending session)
git log -1 --pretty=format:"%H %s"
```

---

## Notes for Next AI / Next Session

<!-- Add any context, gotchas, or decisions that aren't obvious from the code -->

### Decisions Made
- Using Neo4j **AuraDB free tier** for cloud deployment; local dev uses Docker neo4j image
- Ethics middleware is in `backend/app/middleware/ethics_guard.py` — do NOT remove or disable it
- All generated persons have `_synthetic: true` in their metadata JSONB column
- Frontend runs on port 5173 (Vite default); backend on 8000 (FastAPI default)

### Gotchas
- The AuraDB free tier has a **1GB storage limit** — keep synthetic dataset under ~50k entities
- Neo4j Docker image requires `NEO4J_AUTH=neo4j/changeme` env var (not just password)
- Vite proxies `/api` to backend in dev — see `vite.config.ts` proxy config

### Open Questions / Decisions Deferred
- [ ] Should anomaly scores be pre-computed on generation or computed on-demand? (leaning: pre-compute in Phase 3)
- [ ] Do we need pagination on the graph endpoint? (yes, for large datasets in Phase 5)
- [ ] Export format for reports: PDF vs CSV? (defer to Phase 4)

---

*Update this file before ending every session. Commit it with your last commit.*
