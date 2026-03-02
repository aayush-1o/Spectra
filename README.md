# Spectra (SimSight)

![Synthetic Data Only](https://img.shields.io/badge/DATA-SYNTHETIC%20ONLY-red?style=for-the-badge)
![No Real Surveillance](https://img.shields.io/badge/NO-REAL%20SURVEILLANCE-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

> ⚠️ **All data in Spectra is 100% computer-generated and fake.**
> It does not watch, track, or surveil real people. Educational use only.

---

## What Is Spectra?

**Spectra** is a full-stack portfolio project that simulates the kind of data-analytics platform built by companies like Palantir — but constructed entirely on **synthetic, AI-generated data**.

No real person's name, location, or communication ever enters the system. Every person, event, and location is invented by the data generation engine using Faker + NumPy.

### Why build this?

To demonstrate production-level skills across the full stack:

- Async Python backend (FastAPI + SQLAlchemy + Alembic)
- Multi-database architecture (PostgreSQL + Neo4j + Redis)
- Machine learning anomaly detection (IsolationForest, z-score)
- Graph database queries (Cypher, async Neo4j driver)
- React 19 frontend with TypeScript, Tailwind CSS v4
- Interactive visualisations: Leaflet map + Cytoscape graph
- JWT authentication with protected routes
- Dockerised dev environment with health checks

---

## Live Demo

> Run locally — see **Quick Start** below.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🧑 Synthetic People | ✅ | Personas with names, ages, occupations, locations |
| 📍 Fake Locations | ✅ | Fictional lat/lon pins rendered on an interactive map |
| 📞 Fake Events | ✅ | Calls, messages, meetings, transfers with metadata |
| 🕸️ Relationship Graph | ✅ | N-hop Neo4j graph viewer — who knows who |
| 🚨 Anomaly Detection | ✅ | IsolationForest + z-score; Redis-cached results |
| 🗺️ Map View | ✅ | React-Leaflet map with location pins and event popups |
| 🔍 Person Search | ✅ | Debounced search → person cards → graph view |
| 📊 Dashboard | ✅ | KPI cards (persons, events, anomalies) + events feed |
| 🔐 Auth | ✅ | JWT login/register, protected routes, auto-redirect |
| 🛡️ Ethics Layer | ✅ | Persistent banner + PII-rejection middleware on every response |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite 7 + Tailwind CSS v4 |
| Graph Visualisation | Cytoscape.js |
| Map | React-Leaflet + Leaflet.js |
| HTTP Client | Axios (JWT interceptor + 401 auto-redirect) |
| Backend | FastAPI 0.115 (Python 3.11) |
| ORM / Migrations | SQLAlchemy 2 (async) + Alembic |
| Primary DB | PostgreSQL 15 |
| Graph DB | Neo4j 5 (async driver) |
| Cache | Redis 7 |
| Data Generation | Faker + NumPy |
| Anomaly ML | Scikit-learn (IsolationForest) |
| Auth | JWT (python-jose) + bcrypt |
| Testing | Pytest 8 + Vitest 4 + React Testing Library |
| Infrastructure | Docker Compose |

---

## Project Phases

| Phase | Name | Status |
|-------|------|--------|
| 0 | Architecture + Repo Setup | ✅ Complete |
| 1 | Core Infrastructure (DB, Auth, Middleware) | ✅ Complete |
| 2 | Synthetic Data Engine | ✅ Complete |
| 3 | Graph Relationships + Anomaly Detection | ✅ Complete |
| 4 | Frontend + Backend Integration | ✅ Complete |
| 5 | Optimisation | 🔲 Planned |
| 6 | Testing + Hardening | 🔲 Planned |
| 7 | Deployment | 🔲 Planned |
| 8 | Documentation + Mastery | 🔲 Planned |

---

## Quick Start (Local)

### Prerequisites
- **Docker Desktop** (runs Postgres, Redis, Neo4j, backend)
- **Node.js 20+** (for the React frontend)

### 1. Clone + configure

```bash
git clone https://github.com/aayush-1o/Spectra.git
cd Spectra
cp .env.example .env          # edit if needed — defaults work out of the box
```

### 2. Start all backend services

```bash
docker compose up --build -d
# Starts: spectra-postgres, spectra-redis, spectra-neo4j, spectra-backend
# Wait ~30s for Neo4j to fully initialise
```

### 3. Run database migrations

```bash
docker exec spectra-backend alembic upgrade head
```

### 4. Generate synthetic data

```bash
# ~200 persons, 800 events, 50 locations
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# Build the Neo4j graph from Postgres events
docker exec spectra-backend python -m app.data_gen.graph_builder
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 6. Register + explore

Navigate to **http://localhost:5173**, register an account, and explore:

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

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | ❌ | Create account |
| POST | `/api/v1/auth/login` | ❌ | Get JWT token |
| GET | `/api/v1/persons` | ✅ | List synthetic persons |
| GET | `/api/v1/events` | ✅ | List synthetic events |
| GET | `/api/v1/locations` | ✅ | List synthetic locations |
| GET | `/api/v1/graph/neighbourhood/{id}` | ✅ | N-hop graph |
| GET | `/api/v1/graph/centrality` | ✅ | Degree centrality |
| GET | `/api/v1/anomalies` | ✅ | List anomaly records |
| POST | `/api/v1/anomalies/run-detection` | ✅ | Run IsolationForest |

Interactive docs: **http://localhost:8000/docs**

---

## Running Tests

```bash
# Backend — unit tests (22 passing)
docker exec spectra-backend pytest tests/unit/ -v

# Frontend — unit tests (8 passing)
cd frontend && npm run test
```

---

## Project Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design + tech choices |
| [HANDOFF.md](docs/HANDOFF.md) | Session-by-session progress tracker |
| [PHASE-2-EXPLANATION.md](docs/PHASE-2-EXPLANATION.md) | Data generation deep dive |
| [PHASE-3-EXPLANATION.md](docs/PHASE-3-EXPLANATION.md) | Neo4j + anomaly detection explained |
| [PHASE-4-EXPLANATION.md](docs/PHASE-4-EXPLANATION.md) | Frontend architecture + debugging |
| [DEFINITION_OF_DONE.md](docs/DEFINITION_OF_DONE.md) | Per-phase completion criteria |

---

## Ethics

> **Spectra uses only 100% synthetic data.**
> No real person's information is collected, stored, or processed.
> This project cannot and does not surveil real human beings.
> It was built solely to demonstrate software engineering skills.

---

## License

MIT © 2025 — See [LICENSE](LICENSE)
