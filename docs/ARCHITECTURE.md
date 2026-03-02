# SimSight — Architecture Document

> ⚠️ **ETHICS NOTICE — READ FIRST**
> SimSight uses **only computer-generated, 100% synthetic (fake) data**.
> It does not collect, store, or process any real personal information.
> It does not watch, track, or surveil any real human beings.
> This project exists solely to demonstrate technical skills.
> Every screen in the application displays this notice prominently.

---

## 1. System Overview

SimSight is a full-stack web application that **simulates** the kind of data-analytics platform used by companies such as Palantir — but built entirely on synthetic data that the system generates itself. No real person's data ever enters the system.

The system has four logical layers:

1. **Data Generation Layer** — A Python engine that mints thousands of fake entities (people, locations, events, transactions) using libraries like `Faker` and `NumPy`. Data is persisted in a relational database and a graph database.
2. **Backend API Layer** — A FastAPI service that exposes structured REST endpoints for querying entities, relationships, events, and anomaly scores.
3. **Graph & Analytics Layer** — NetworkX (Python) builds in-memory relationship graphs; a lightweight anomaly detection module flags unusual synthetic patterns using statistical thresholds (z-score, isolation forest).
4. **Frontend Dashboard** — A React single-page application featuring an interactive map (Leaflet.js), a relationship graph viewer (Sigma.js / Cytoscape.js), a search/filter panel, and a report export feature.

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              React SPA  (Vite)                           │   │
│  │  ┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │ Dashboard│ │  Map View   │ │ Graph    │ │ Search │  │   │
│  │  │ (KPIs)   │ │ (Leaflet)   │ │ (Sigma)  │ │ Panel  │  │   │
│  │  └──────────┘ └─────────────┘ └──────────┘ └────────┘  │   │
│  └─────────────────────┬────────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │ HTTPS / REST (JSON)
┌────────────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend  (Python 3.11)                 │
│  ┌────────────┐  ┌───────────────┐  ┌───────────────────────┐   │
│  │  Entities  │  │  Graph API    │  │  Anomaly Detection    │   │
│  │  Router    │  │  Router       │  │  Router               │   │
│  └─────┬──────┘  └──────┬────────┘  └──────────┬────────────┘   │
│        │                │                       │                │
│  ┌─────▼────────────────▼───────────────────────▼────────────┐  │
│  │                   Service Layer                            │  │
│  │  EntityService │ GraphService │ AnomalyService             │  │
│  └──────┬──────────────────────┬──────────────────────────────┘  │
│         │                      │                                 │
│  ┌──────▼──────┐       ┌───────▼──────────────────────────────┐  │
│  │  PostgreSQL  │       │  Neo4j (free AuraDB or local docker) │  │
│  │  (primary   │       │  (relationship graph storage)        │  │
│  │   store)    │       └──────────────────────────────────────┘  │
│  └─────────────┘                                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │           Data Generation Engine  (scripts/)             │    │
│  │  Faker │ NumPy │ NetworkX │ custom generators            │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Full Tech Stack

| Layer | Technology | Role in SimSight | Why This Choice | Tradeoffs vs Alternatives |
|---|---|---|---|---|
| **Frontend Framework** | React 18 + Vite | SPA shell, routing, state management | Largest ecosystem, fast HMR, great hiring signal | Vue 3 is lighter; Next.js adds SSR complexity not needed here |
| **Map Library** | Leaflet.js + React-Leaflet | Interactive synthetic-location map | Free, MIT, no API key needed; excellent docs | Mapbox/Google Maps need paid keys; Deck.gl is overkill |
| **Graph Visualisation** | Cytoscape.js | Relationship graph (persons ↔ events) | Handles 10k+ nodes, good layout algorithms, free | D3 force graph is lower-level (more work); Sigma.js is faster but less flexible |
| **UI Component Library** | shadcn/ui + Tailwind CSS | Pre-built accessible components | Copy-paste components, zero bundle bloat, modern look | MUI/Ant are heavier and opinionated |
| **HTTP Client** | Axios | API calls from frontend | Promise-based, interceptors for global error handling | fetch() is fine but lacks interceptors |
| **Backend Framework** | FastAPI (Python 3.11) | REST API, validation, OpenAPI docs | Auto-generates docs, async-native, Python ecosystem matches data science tools | Django REST is heavier; Flask lacks typing |
| **ORM** | SQLAlchemy 2 + Alembic | DB models & migrations | Industry standard, great async support | Tortoise ORM is lighter but less mature |
| **Primary Database** | PostgreSQL 15 | Entities, events, metadata | ACID, JSON columns, full-text search, free everywhere | SQLite easier locally but not production-ready; MySQL similar but less featureful |
| **Graph Database** | Neo4j (AuraDB free tier) | Store & query relationship graphs | Cypher query language is expressive, free tier sufficient for demo | NetworkX in-memory only; AgensGraph is less popular |
| **Cache** | Redis (Upstash free tier) | Cache heavy graph traversals, rate-limit | 30ms vs 300ms on repeated queries | Memcached has no persistence; in-process cache doesn't survive restarts |
| **Data Generation** | Faker + NumPy + NetworkX | Synthetic person/event/location creation | Faker is purpose-built for realistic fake data; NumPy for distributions | random stdlib lacks realistic names/addresses |
| **Anomaly Detection** | Scikit-learn (IsolationForest, Z-score) | Flag unusual patterns in synthetic events | Lightweight, no infra required, interpretable | TensorFlow/PyTorch are overkill; statistical rules alone miss complex patterns |
| **Auth** | JWT (python-jose) + bcrypt | Protect API endpoints | Stateless, simple to implement, no third-party dependency | OAuth2/Auth0 adds complexity beyond free tier; sessions need sticky routing |
| **Testing** | Pytest + React Testing Library + Vitest | Unit & integration tests | De-facto standards in both ecosystems | Jest alone covers JS; Playwright for E2E can be added later |
| **Containerisation** | Docker + Docker Compose | Reproducible local dev environment | Industry standard, simplifies onboarding | Podman is an alternative but more setup |
| **CI/CD** | GitHub Actions | Lint, test, build, deploy on push | Free for public repos, tight GitHub integration | CircleCI/Travis CI have smaller free tiers |
| **Deployment** | Railway (free tier) | Host backend + DB | Generous free tier, auto-deploys from GitHub, supports Docker | Render is comparable; Heroku removed free tier |
| **Frontend Hosting** | Vercel (free tier) | Host React SPA | Zero-config Vite deploy, global CDN | Netlify is equivalent; GitHub Pages lacks API proxy |

---

## 4. Component Breakdown

### 4.1 Data Generation Engine (`backend/app/data_gen/`)
Runs as a standalone script (triggered via CLI or a `/admin/generate` API endpoint). Responsibilities:
- Generate `N` fake **Persons** (name, DOB, fake SSN, fake address, occupation)
- Generate fake **Locations** (lat/lon offset from a fictional city centre, building type)
- Generate **Events** (calls, messages, meetings, transfers) between persons at locations
- Write raw entities to PostgreSQL
- Build relationship graph and load into Neo4j
- Compute initial edge weights (call frequency, transaction volume)

### 4.2 Entity Service (`backend/app/services/entity_service.py`)
CRUD for persons, locations, events. Supports full-text search, pagination, and filtering.

### 4.3 Graph Service (`backend/app/services/graph_service.py`)
- Queries Neo4j for N-hop neighbourhoods around a node
- Returns adjacency data serialised for the frontend Cytoscape graph
- Computes centrality metrics (degree, betweenness) on demand

### 4.4 Anomaly Service (`backend/app/services/anomaly_service.py`)
- Reads event time-series from PostgreSQL
- Applies IsolationForest and z-score rules
- Returns flagged entities with score + reason string
- Results cached in Redis for 5 minutes

### 4.5 FastAPI Application (`backend/app/main.py`)
- Mounts routers: `/api/v1/entities`, `/api/v1/graph`, `/api/v1/anomalies`, `/api/v1/admin`
- Global middleware: CORS, request logging, ethics-banner injection
- OpenAPI docs auto-generated at `/docs`

### 4.6 React Frontend (`frontend/src/`)
- **Dashboard page**: KPI cards (total persons, events, anomalies flagged), recent events feed
- **Map page**: Leaflet map showing fake location pins, click → entity info panel
- **Graph page**: Cytoscape graph of relationships, search for a person, expand N hops
- **Anomalies page**: Table of flagged synthetic entities with score and reason
- **Ethics banner**: Persistent top banner + `/about` page explaining fake-data-only policy

---

## 5. Data Model Overview

### Entities (PostgreSQL)

```
Person
  id          UUID PK
  full_name   TEXT
  date_of_birth DATE
  fake_ssn    TEXT  (format XXX-XX-XXXX, flagged as synthetic)
  occupation  TEXT
  created_at  TIMESTAMP

Location
  id          UUID PK
  name        TEXT  (e.g. "Synthetic Tower Block 7")
  lat         FLOAT
  lon         FLOAT
  location_type ENUM(office, residence, transit_hub, unknown)

Event
  id          UUID PK
  event_type  ENUM(call, message, meeting, transfer)
  actor_id    UUID FK → Person
  target_id   UUID FK → Person
  location_id UUID FK → Location (nullable)
  occurred_at TIMESTAMP
  metadata    JSONB  (duration_seconds, amount_usd, etc.)
  anomaly_score FLOAT (null = not yet scored)
```

### Relationships (Neo4j)

```
(:Person)-[:CONTACTED {event_id, weight, ts}]->(:Person)
(:Person)-[:TRANSACTED {event_id, amount, ts}]->(:Person)
(:Person)-[:VISITED {event_id, ts}]->(:Location)
```

### Anomaly Record (PostgreSQL)

```
AnomalyRecord
  id              UUID PK
  entity_id       UUID  (person or event)
  entity_type     ENUM(person, event)
  score           FLOAT
  reason          TEXT
  detected_at     TIMESTAMP
  algorithm       TEXT  (isolation_forest | z_score | rule_based)
```

---

## 6. API Structure

### Entities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/persons` | List persons (paginated, searchable) |
| GET | `/api/v1/persons/{id}` | Get single person + event summary |
| GET | `/api/v1/locations` | List locations |
| GET | `/api/v1/locations/{id}` | Location detail + events at location |
| GET | `/api/v1/events` | List events (filter by type, date range) |
| GET | `/api/v1/events/{id}` | Event detail |

### Graph

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/graph/neighbourhood/{person_id}?hops=2` | N-hop graph for a person |
| GET | `/api/v1/graph/centrality` | Top-N persons by centrality score |
| GET | `/api/v1/graph/shortest-path?from={id}&to={id}` | Shortest path between two persons |

### Anomalies

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/anomalies` | List all flagged records (paginated) |
| GET | `/api/v1/anomalies/{id}` | Anomaly detail |
| POST | `/api/v1/anomalies/run-detection` | Trigger anomaly detection job (admin only) |

### Admin

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/admin/generate` | Generate N synthetic entities |
| DELETE | `/api/v1/admin/reset` | Wipe all synthetic data and regenerate |
| GET | `/api/v1/admin/stats` | Row counts, graph stats |

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register demo user |
| POST | `/api/v1/auth/login` | Login → return JWT |
| GET | `/api/v1/auth/me` | Current user info |

---

## 7. Deployment Architecture

```
GitHub (main branch)
       │
       │  push / PR merge
       ▼
GitHub Actions CI
  ├── Lint (ruff, eslint)
  ├── Unit Tests (pytest, vitest)
  ├── Build Docker image
  └── Deploy ──────► Railway (Backend + PostgreSQL)
                           │
                           ├── FastAPI container
                           ├── PostgreSQL (Railway plugin)
                           └── Redis (Upstash free, external)

                     Vercel (Frontend)
                           │
                           └── React SPA (static)
                                 │ API calls
                                 └────────────► Railway backend
```

Environment variables are managed via Railway's dashboard and Vercel's project settings. Secrets are never committed to Git.

---

## 8. Ethics & Safety Layer

The ethics layer is a **first-class engineering concern**, not a footnote.

| Mechanism | Implementation |
|-----------|----------------|
| **Persistent UI banner** | React component fixed to top of every page: *"⚠️ All data in SimSight is 100% computer-generated and fake. No real people are tracked."* |
| **About / Ethics page** | `/about` route with full explanation: what synthetic data is, why real surveillance harms privacy, and what responsible data practice looks like |
| **API request guard** | Middleware in FastAPI checks every POST/PUT body for patterns that look like real PII (regex for real SSN formats, phone patterns, email addresses). Rejects with `400 ETHICS_VIOLATION` and logs the attempt |
| **README badge** | Bright red badge: `SYNTHETIC DATA ONLY — NO REAL SURVEILLANCE` |
| **ETHICS.md** | Separate file explaining: what this project does, what it does NOT do, why privacy matters, and the risks of real surveillance tools |
| **Data generation watermark** | All generated records include `_synthetic: true` field in JSONB metadata |
| **No external data ingestion** | No file upload endpoint. No web scraping. No external API keys for real data sources |

---

*Document version: 1.0 — Generated for SimSight Phase 0*
