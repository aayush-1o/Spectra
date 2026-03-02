# Spectra (SimSight)

![Synthetic Data Only](https://img.shields.io/badge/DATA-SYNTHETIC%20ONLY-red?style=for-the-badge)
![No Real Surveillance](https://img.shields.io/badge/NO-REAL%20SURVEILLANCE-red?style=for-the-badge)
![Phase 7 Complete](https://img.shields.io/badge/Phase-7%20Complete-brightgreen?style=for-the-badge)
![CI](https://github.com/aayush-1o/Spectra/actions/workflows/ci.yml/badge.svg?branch=dev)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

> ⚠️ **All data in Spectra is 100% computer-generated and fake.**
> It does not watch, track, or surveil real people. Educational use only.

---

## What Is Spectra?

**Spectra** is a full-stack portfolio project that simulates the kind of data-analytics platform built by companies like Palantir — constructed entirely on **synthetic, AI-generated data**.

No real person's name, location, or communication ever enters the system. Every person, event, and location is invented by the data generation engine using Faker + NumPy.

### Why build this?

To demonstrate production-level skills across the full stack:

- Async Python backend (FastAPI + SQLAlchemy 2 + Alembic)
- Multi-database architecture (PostgreSQL + Neo4j + Redis)
- Machine learning anomaly detection (IsolationForest, z-score)
- Graph database queries (Cypher, async Neo4j driver)
- React 18 frontend with TypeScript, code-splitting, lazy loading
- Interactive visualisations: Leaflet map + Cytoscape graph
- JWT authentication with protected routes
- Multi-stage Docker builds (production-grade image sizes)
- Redis caching with graceful fallback strategy
- Observability middleware (request timing, slow query logging)

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend | https://spectra-simsight.vercel.app |
| Backend API | https://spectra-api.onrender.com |
| Health | https://spectra-api.onrender.com/health |

> **Note:** Render free tier spins down after 15 min of inactivity. First request after idle may take ~30s.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🧑 Synthetic People | ✅ | Personas with names, ages, occupations, locations |
| 📍 Fake Locations | ✅ | Fictional lat/lon pins rendered on an interactive map |
| 📞 Fake Events | ✅ | Calls, messages, meetings, transfers with metadata |
| 🕸️ Relationship Graph | ✅ | N-hop Neo4j graph viewer — who knows who |
| 🚨 Anomaly Detection | ✅ | IsolationForest + z-score; deduplicated results |
| 🗺️ Map View | ✅ | React-Leaflet map with location pins and event popups |
| 🔍 Person Search | ✅ | Debounced search → person cards → graph view |
| 📊 Dashboard | ✅ | KPI cards (persons, events, anomalies) + events feed |
| 🔐 Auth | ✅ | JWT login/register, protected routes, auto-redirect |
| 🛡️ Ethics Layer | ✅ | Persistent banner + PII-rejection middleware on every response |
| ⚡ Redis Cache | ✅ | Neighbourhood queries, KPI counts cached; graceful fallback |
| 📈 Metrics API | ✅ | `GET /api/v1/admin/metrics` — live performance snapshot |
| 🕐 Request Timing | ✅ | `X-Response-Time-Ms` header + slow-query logging (>200ms) |
| 🐳 Production Docker | ✅ | Multi-stage images: backend ~350MB, frontend ~25MB (nginx) |
| 🔀 Code Splitting | ✅ | React.lazy + Suspense for heavy pages (~40% smaller initial bundle) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS |
| Graph Visualisation | Cytoscape.js |
| Map | React-Leaflet + Leaflet.js |
| HTTP Client | Axios (JWT interceptor + 401 auto-redirect) |
| Backend | FastAPI 0.115 (Python 3.11) |
| ORM / Migrations | SQLAlchemy 2 (async) + Alembic |
| Primary DB | PostgreSQL 15 (GIN trigram index for fast ILIKE search) |
| Graph DB | Neo4j 5 (async driver, startup indexes) |
| Cache | Redis 7 (shared pool, CacheHelper fallback) |
| Data Generation | Faker + NumPy |
| Anomaly ML | Scikit-learn (IsolationForest + z-score) |
| Auth | JWT (python-jose) + bcrypt |
| Testing | Pytest 8 + Vitest + React Testing Library |
| Infrastructure | Docker Compose + multi-stage Dockerfiles + nginx |

---

## Project Phases

| Phase | Name | Status |
|-------|------|--------|
| 0 | Architecture + Repo Setup | ✅ Complete |
| 1 | Core Infrastructure (DB, Auth, Middleware) | ✅ Complete |
| 2 | Synthetic Data Engine | ✅ Complete |
| 3 | Graph Relationships + Anomaly Detection | ✅ Complete |
| 4 | Frontend + Backend Integration | ✅ Complete |
| 5 | Optimisation | ✅ Complete |
| 6 | Testing + Hardening | ✅ Complete |
| 7 | Deployment | ✅ **Complete** |
| 8 | Documentation + Mastery | 🔲 Planned |

---

## Quick Start (Local)

### Prerequisites
- **Docker Desktop** (runs Postgres, Redis, Neo4j, backend)
- **Node.js 20+** (for local frontend dev)

### 1. Clone + configure

```bash
git clone https://github.com/aayush-1o/Spectra.git
cd Spectra
cp .env.example .env          # defaults work out of the box
```

### 2. Start all backend services

```bash
docker compose up --build -d
# Dev: starts postgres, redis, neo4j, backend, frontend (nginx)

# Production (cloud managed DBs, no local DBs):
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Run database migrations

```bash
docker exec spectra-backend alembic upgrade head
# Applies all migrations including Phase 5 performance indexes
```

### 4. Generate synthetic data

```bash
# ~200 persons, 800 events, 50 locations
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# Build the Neo4j graph from Postgres events
docker exec spectra-backend python -m app.data_gen.graph_builder
```

### 5. Access the app

| Mode | URL | Notes |
|------|-----|-------|
| **Production (Docker)** | http://localhost | nginx serves compiled React app |
| **Dev (hot-reload)** | http://localhost:5173 | `cd frontend && npm install && npm run dev` |

### 6. Register + explore

Navigate to the app, register an account, and explore:

| URL | Page |
|-----|------|
| `/` | Dashboard — KPI cards + events feed |
| `/map` | Leaflet map of synthetic locations |
| `/graph` | Graph explorer (search → Cytoscape) |
| `/anomalies` | Anomaly table + run detection |
| `/search` | Person search |
| `/about` | Ethics statement |

---

## API Reference

Base URL: `http://localhost:8000`

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | ❌ | Create account |
| POST | `/api/v1/auth/login` | ❌ | Get JWT token |
| GET | `/api/v1/auth/me` | ✅ | Current user info |

### Entities

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/persons` | ✅ | List synthetic persons (GIN-indexed search) |
| GET | `/api/v1/persons/{id}` | ✅ | Single person detail |
| GET | `/api/v1/events` | ✅ | List events (filter by type, date range) |
| GET | `/api/v1/locations` | ✅ | List synthetic locations |

### Graph

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/graph/neighbourhood/{id}` | ✅ | N-hop graph (Redis-cached 120s) |
| GET | `/api/v1/graph/centrality` | ✅ | Degree centrality ranking |
| GET | `/api/v1/graph/shortest-path` | ✅ | Shortest path between two persons |

### Anomalies

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/anomalies` | ✅ | List anomaly records (deduplicated) |
| GET | `/api/v1/anomalies/{id}` | ✅ | Single anomaly detail |
| POST | `/api/v1/anomalies/run-detection` | ✅ | Run IsolationForest + z-score |

### Admin (Phase 5)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/admin/metrics` | ✅ | Performance snapshot + cache stats |

Interactive docs: **http://localhost:8000/docs**

---

## Phase 5 — What Was Optimised

### Performance Gains

| Area | Before | After | Gain |
|------|--------|-------|------|
| `ILIKE` person search | ~45ms (seq scan) | ~3ms (GIN index) | **~15×** |
| Graph neighbourhood (cold) | ~150ms | ~80ms | **~2×** |
| Graph neighbourhood (warm/cached) | N/A | ~3ms | **~50×** |
| Anomaly deduplication | Creates duplicates | 0 inserts on repeat | **Bug fixed** |
| Redis connection overhead | ~2ms/req (new conn) | ~0.1ms (pooled) | **~20×** |
| Backend Docker image | ~820MB | ~350MB | **57% smaller** |
| Frontend Docker image | N/A | ~25MB (nginx) | **Production-ready** |
| Initial JS bundle | 100% loaded upfront | ~60% (40% lazy) | **40% reduction** |

### Key Changes
- **GIN trigram index** on `persons.fake_name` — `ILIKE '%search%'` now uses an index scan
- **Unique DB constraint** on `anomaly_records(entity_id, algorithm)` — no more duplicate detection runs
- **Shared Redis pool** (20 connections) with graceful `RedisError` fallback
- **Neighbourhood caching** — Redis key `graph:neighbourhood:{id}:{hops}` (TTL 120s)
- **Neo4j startup indexes** on `Person(id)` and `Location(id)`
- **`TimingMiddleware`** — logs slow requests (>200ms), adds `X-Response-Time-Ms` header
- **`GET /api/v1/admin/metrics`** — real-time KPIs, cache hit rate, avg response time
- **Multi-stage Dockerfiles** — build tools excluded from runtime images
- **React.lazy + Suspense** code splitting for all heavy pages

---

## Running Tests

```bash
# All backend tests (47 tests, all passing)
docker exec spectra-backend pytest tests/ -v

# Phase 5 specific tests
docker exec spectra-backend pytest \
  tests/unit/test_performance.py \
  tests/unit/test_redis_fallback.py \
  tests/unit/test_indexes.py \
  tests/unit/test_timing_middleware.py \
  -v

# Frontend tests
cd frontend && npm run test
```

---

## Project Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design + tech choices |
| [HANDOFF.md](docs/HANDOFF.md) | Phase-by-phase progress tracker |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Step-by-step deployment guide |
| [PHASE-2-EXPLANATION.md](docs/PHASE-2-EXPLANATION.md) | Data generation deep dive |
| [PHASE-3-EXPLANATION.md](docs/PHASE-3-EXPLANATION.md) | Neo4j + anomaly detection explained |
| [PHASE-4-EXPLANATION.md](docs/PHASE-4-EXPLANATION.md) | Frontend architecture + debugging |
| [PHASE-5-EXPLANATION.md](docs/PHASE-5-EXPLANATION.md) | Optimisation: benchmarks, Redis keys, debugging guide |
| [PHASE-7-EXPLANATION.md](docs/PHASE-7-EXPLANATION.md) | Deployment: infra diagram, CI/CD, security checklist |
| [DEFINITION_OF_DONE.md](docs/DEFINITION_OF_DONE.md) | Per-phase completion criteria |

---

## Redis Cache Key Reference

| Key | TTL | Content |
|-----|-----|---------|
| `anomaly:last_run` | 300s | Last detection run summary |
| `graph:neighbourhood:{id}:{hops}` | 120s | Serialised neighbourhood graph |
| `dashboard:kpis` | 60s | Person / event / anomaly counts |

---

## Ethics

> **Spectra uses only 100% synthetic data.**
> No real person's information is collected, stored, or processed.
> This project cannot and does not surveil real human beings.
> It was built solely to demonstrate software engineering skills.

See [ETHICS.md](ETHICS.md) for the full ethics statement.

---

## License

MIT © 2025 — See [LICENSE](LICENSE)
