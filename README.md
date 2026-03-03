# Spectra (SimSight)

![Synthetic Data Only](https://img.shields.io/badge/DATA-SYNTHETIC%20ONLY-red?style=for-the-badge)
![No Real Surveillance](https://img.shields.io/badge/NO-REAL%20SURVEILLANCE-red?style=for-the-badge)
![Phase 10 Complete](https://img.shields.io/badge/Phase-10%20Complete-brightgreen?style=for-the-badge)
![CI](https://github.com/aayush-1o/Spectra/actions/workflows/ci.yml/badge.svg?branch=dev)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![CesiumJS](https://img.shields.io/badge/CesiumJS-3D%20Globe-6CADDF?style=for-the-badge)
![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

> ⚠️ **All data in Spectra is 100% computer-generated and fake.**
> It does not watch, track, or surveil real people. Educational use only.

---

## What Is Spectra?

**Spectra** is a full-stack portfolio project that simulates the kind of data-analytics platform built by companies like Palantir — constructed entirely on **synthetic, AI-generated data**.

No real person's name, location, or communication ever enters the system. Every person, event, location, and asset position is invented by the data generation engine using Faker + NumPy.

### Why build this?

To demonstrate production-level skills across the full stack:

- Async Python backend (FastAPI + SQLAlchemy 2 + Alembic)
- Multi-database architecture (PostgreSQL + Neo4j + Redis)
- Machine learning anomaly detection (IsolationForest, z-score, DBSCAN, LOF)
- Graph database queries (Cypher, async Neo4j driver, Louvain community detection)
- React 18 frontend with TypeScript, code-splitting, lazy loading
- **3D globe intelligence platform** — CesiumJS + Resium with real-time asset tracking
- Interactive visualisations: CesiumJS 3D globe, Leaflet map + heatmap, Cytoscape graph
- JWT authentication with protected routes
- **AI-powered NL search and intelligence summaries** (Anthropic Claude Sonnet)
- **Person risk scoring** (composite 4-factor model)
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
| 🌍 **3D Globe Tracking** | ✅ | CesiumJS rotating Earth — flights, drones & vehicles tracked in real-time |
| 🎯 **Visual Intel Modes** | ✅ | Normal / Night Vision / Thermal / Tactical — CSS filter overlays |
| 🛰 **Classification HUD** | ✅ | `TS // SI-TK // NOFORN` banner, UTC clock, cursor coordinates overlay |
| 🧑 Synthetic People | ✅ | Personas with names, ages, occupations, nationalities, aliases, phone numbers |
| 📍 Fake Locations | ✅ | Fictional lat/lon pins with district, threat level, surveillance coverage |
| 📞 Fake Events | ✅ | Calls, messages, meetings, transfers — all with rich metadata |
| 🕸️ Relationship Graph | ✅ | N-hop Neo4j graph viewer — nodes colored by **risk score** or **community** |
| 🔴 Person Risk Score | ✅ | Composite 0-100 score (volume, off-hours, transfer size, anomaly count) |
| 🚨 Anomaly Detection | ✅ | IsolationForest + z-score + DBSCAN + LOF + Night Owl Rule |
| 🫧 Community Detection | ✅ | Louvain algorithm on Neo4j graph — cached in Redis |
| 🗺️ Map View | ✅ | React-Leaflet map with **location pins** AND **activity heatmap** toggle |
| ✨ AI NL Search | ✅ | Natural language query → Claude Sonnet → structured SQL filters |
| 🤖 AI Intelligence Brief | ✅ | Claude generates a 2-3 paragraph analyst report per person |
| 👤 Person Detail Page | ✅ | Full profile with timeline, AI summary, risk badge, graph link |
| 📅 Entity Timeline | ✅ | Vertical chronological event history with anomaly flags |
| 🔍 Person Search | ✅ | Name search + AI NL search tab in one unified page |
| 📊 Dashboard | ✅ | KPI cards (persons, events, anomalies) + events feed |
| 🔐 Auth | ✅ | JWT login/register, protected routes, auto-redirect |
| 🛡️ Ethics Layer | ✅ | Persistent banner + PII-rejection middleware on every response |
| ⚡ Redis Cache | ✅ | Neighbourhood, community, KPI counts cached; graceful fallback |
| 📈 Metrics API | ✅ | `GET /api/v1/admin/metrics` — live performance snapshot |
| 🐳 Production Docker | ✅ | Multi-stage images: backend ~350MB, frontend ~25MB (nginx) |
| 🔀 Code Splitting | ✅ | React.lazy + Suspense for heavy pages (~40% smaller initial bundle) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS |
| **3D Globe** | **CesiumJS + Resium** (React wrapper) — Cesium Ion World Imagery |
| Graph Visualisation | Cytoscape.js (risk + community coloring) |
| Map | React-Leaflet + leaflet.heat (heatmap) |
| HTTP Client | Axios (JWT interceptor + 401 auto-redirect) |
| Backend | FastAPI 0.115 (Python 3.11) |
| ORM / Migrations | SQLAlchemy 2 (async) + Alembic |
| Primary DB | PostgreSQL 15 (GIN trigram index for fast ILIKE search) |
| Graph DB | Neo4j 5 (async driver, Louvain community detection) |
| Cache | Redis 7 (shared pool, CacheHelper fallback) |
| Data Generation | Faker + NumPy |
| Anomaly ML | Scikit-learn (IsolationForest, z-score, DBSCAN, LOF) |
| AI / NLP | **Anthropic Claude Sonnet** (NL search + intelligence summaries) |
| Graph Analysis | NetworkX + python-louvain |
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
| 7 | Deployment | ✅ Complete |
| 8 | AI + Risk Intelligence Layer | ✅ Complete |
| 9 | Real-Time Asset Tracking (WebSocket + Deck.gl) | ✅ Complete |
| **10** | **CesiumJS 3D Globe Intelligence Platform** | ✅ **Complete** |

---

## Quick Start (Local)

### Prerequisites
- **Docker Desktop** (runs Postgres, Redis, Neo4j, backend)
- **Node.js 20+** (for local frontend dev)
- **Cesium Ion account** (free — get token at [ion.cesium.com](https://ion.cesium.com))
- **Anthropic API key** (optional — AI features degrade gracefully without it)

### 1. Clone + configure

```bash
git clone https://github.com/aayush-1o/Spectra.git
cd Spectra
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and VITE_CESIUM_TOKEN
```

### 2. Start all backend services

```bash
docker compose up --build -d
```

### 3. Run database migrations

```bash
docker exec spectra-backend alembic upgrade head
```

### 4. Generate synthetic data

```bash
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800
docker exec spectra-backend python -m app.data_gen.graph_builder
```

### 5. Compute initial risk scores

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/compute-risk-scores
```

### 6. Run the frontend

```bash
cd frontend
npm install       # installs cesium, resium, vite-plugin-static-copy
npm run dev
```

### 7. Explore

| URL | Page |
|-----|------|
| `/` | Dashboard — KPI cards + events feed |
| `/live-map` | **3D CesiumJS Globe** — real-time asset tracking |
| `/map` | Leaflet map — pins **or** activity heatmap |
| `/graph` | Graph explorer — risk score **or** community coloring |
| `/anomalies` | Anomaly table (IsolationForest, DBSCAN, LOF, Night Owl) |
| `/search` | Name search **or** ✨ AI NL search tab |
| `/person/:id` | Full person profile — AI summary + event timeline |
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
| GET | `/api/v1/persons/{id}` | ✅ | Single person with all Phase 8 fields |
| GET | `/api/v1/persons/{id}/summary` | ✅ | Claude AI intelligence report |
| GET | `/api/v1/events` | ✅ | List events (filter by type, date range, person_id) |
| GET | `/api/v1/locations` | ✅ | List synthetic locations (district, threat_level) |

### Real-Time Asset Stream

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| WS | `/api/v1/stream/assets` | ❌ | WebSocket — 1 Hz position broadcast |
| GET | `/api/v1/stream/assets/snapshot` | ❌ | REST snapshot of current positions |

### AI Search

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/search/nl` | ✅ | NL query → Claude → SQL filters → persons |

### Graph

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/graph/neighbourhood/{id}` | ✅ | N-hop graph (Redis-cached 120s) |
| GET | `/api/v1/graph/centrality` | ✅ | Degree centrality ranking |
| GET | `/api/v1/graph/shortest-path` | ✅ | Shortest path between two persons |
| GET | `/api/v1/graph/communities` | ✅ | Louvain community assignments (Redis-cached 600s) |

### Anomalies

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/anomalies` | ✅ | List anomaly records (deduplicated) |
| POST | `/api/v1/anomalies/run-detection` | ✅ | Run all detectors |

### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/admin/metrics` | ✅ | Performance snapshot + cache stats |
| POST | `/api/v1/admin/compute-risk-scores` | ✅ | Batch-compute risk scores for all persons |

Interactive docs: **http://localhost:8000/docs**

---

## Environment Variables

| Variable | Required | Where Used |
|----------|----------|-----------:|
| `DATABASE_URL` | ✅ Always | Postgres connection |
| `NEO4J_URI` | ✅ Always | Neo4j connection |
| `NEO4J_USERNAME` | ✅ Always | Neo4j auth |
| `NEO4J_PASSWORD` | ✅ Always | Neo4j auth |
| `REDIS_URL` | ✅ Always | Redis connection |
| `JWT_SECRET_KEY` | ✅ Always | Auth tokens |
| `ANTHROPIC_API_KEY` | ⚡ AI features | NL Search + AI Summary |
| `VITE_API_BASE_URL` | ✅ Frontend | Backend API URL |
| `VITE_CESIUM_TOKEN` | ✅ **Globe** | **Cesium Ion world imagery token** |

---

## Redis Cache Key Reference

| Key | TTL | Content |
|-----|-----|---------|
| `anomaly:last_run` | 300s | Last detection run summary |
| `graph:neighbourhood:{id}:{hops}` | 120s | Serialised neighbourhood graph |
| `dashboard:kpis` | 60s | Person / event / anomaly counts |
| `graph:communities` | 600s | Louvain partition dict |

---

## Running Tests

```bash
# All backend tests
docker exec spectra-backend pytest tests/ -v

# Phase 9 unit tests (WebSocket stream, telemetry)
docker exec spectra-backend pytest tests/test_phase9.py -v

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
| [PHASE-10-EXPLANATION.md](docs/PHASE-10-EXPLANATION.md) | **NEW** CesiumJS 3D globe deep dive |
| [PHASE-9-EXPLANATION.md](docs/PHASE-9-EXPLANATION.md) | WebSocket real-time tracking |
| [PHASE-8-EXPLANATION.md](docs/PHASE-8-EXPLANATION.md) | AI, risk scoring, community detection |
| [PHASE-7-EXPLANATION.md](docs/PHASE-7-EXPLANATION.md) | Deployment: infra, CI/CD, security |
| [PHASE-5-EXPLANATION.md](docs/PHASE-5-EXPLANATION.md) | Optimisation: benchmarks, Redis keys |

---

## Ethics

> **Spectra uses only 100% synthetic data.**
> No real person's information is collected, stored, or processed.
> This project cannot and does not surveil real human beings.
> It was built solely to demonstrate software engineering skills.

---

## License

MIT © 2025 — See [LICENSE](LICENSE)
