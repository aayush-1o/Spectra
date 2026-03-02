# SimSight — Definition of Done (Per Phase)

> A phase is **not complete** until every item in its DoD checklist is checked.
> Do not start the next phase until the current one is done.
> Update the HANDOFF.md when you finish each phase.

---

## Phase 0 — Architecture + Repo Setup

**Goal**: All planning documents written and repository skeleton exists.

### Checklist
- [ ] `docs/ARCHITECTURE.md` written and covers all 8 sections
- [ ] `docs/HANDOFF.md` template populated with Phase 0 details
- [ ] `docs/FOLDER_STRUCTURE.md` written
- [ ] `docs/GIT_BRANCH_STRATEGY.md` written
- [ ] `docs/DEFINITION_OF_DONE.md` written (this file)
- [ ] `ETHICS.md` written at repo root
- [ ] GitHub repository created (public)
- [ ] `main` and `dev` branches exist
- [ ] `.gitignore` committed to `main`
- [ ] `.env.example` committed with all variable names (no real values)
- [ ] `README.md` has project name, ethics badge, and "coming soon" scaffold
- [ ] Initial commit tagged `v0.0.1`

### Definition of Complete
> The GitHub repo is publicly visible, has a clean initial commit, all five docs exist in `docs/`, and a collaborator could understand the project's purpose and structure just from reading the README and ARCHITECTURE.md.

---

## Phase 1 — Core Setup

**Goal**: A running local environment with database, auth, and empty API scaffolds.

### Checklist
- [ ] `docker-compose.yml` starts PostgreSQL, Redis, and the FastAPI backend
- [ ] FastAPI app starts with no errors (`GET /health` returns `{"status": "ok"}`)
- [ ] All SQLAlchemy models defined: `Person`, `Location`, `Event`, `AnomalyRecord`, `User`
- [ ] Alembic migration `0001_initial_schema.py` runs without error: `alembic upgrade head`
- [ ] Auth endpoints implemented and tested:
  - `POST /api/v1/auth/register` → creates user, returns JWT
  - `POST /api/v1/auth/login` → validates credentials, returns JWT
  - `GET /api/v1/auth/me` → returns current user (requires valid JWT)
- [ ] Ethics guard middleware wired up (returns `400` on fake PII patterns)
- [ ] React + Vite scaffold runs: `npm run dev` opens at `localhost:5173`
- [ ] Frontend shows placeholder dashboard with ethics banner visible
- [ ] `.env.example` updated with any new variables added
- [ ] All code on `dev` branch, feature branch merged

### How to Test Completion
```bash
docker compose up --build
# → No error output

curl http://localhost:8000/health
# → {"status": "ok"}

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo1234"}'
# → {"access_token": "...", "token_type": "bearer"}

# Open http://localhost:5173 → see placeholder page with ethics banner
```

### Definition of Complete
> Running `docker compose up` followed by Alembic migration produces a healthy API, a working database, and a React app that loads in the browser with the ethics banner visible.

---

## Phase 2 — Synthetic Data Engine

**Goal**: The system can generate thousands of realistic-looking fake entities and persist them.

### Checklist
- [ ] `PersonGenerator` creates fake persons with: name, DOB, fake SSN, occupation, address
- [ ] `LocationGenerator` creates fake locations within a fictional bounding box with building types
- [ ] `EventGenerator` creates events (calls, messages, meetings, transfers) with realistic time distributions
- [ ] Events are distributed across persons and locations using weighted random selection
- [ ] Data written to PostgreSQL via SQLAlchemy within a single transaction per batch
- [ ] Generation script: `python -m app.data_gen.run --persons 500 --events 2000` completes without error
- [ ] All generated records have `"_synthetic": true` in their `metadata` JSONB field
- [ ] `GET /api/v1/persons` returns paginated person list
- [ ] `GET /api/v1/locations` returns paginated location list
- [ ] `GET /api/v1/events` returns paginated event list with filtering by type + date
- [ ] Unit tests: `pytest tests/unit/test_person_generator.py` → all pass
- [ ] Unit tests: `pytest tests/unit/test_event_generator.py` → all pass

### How to Test Completion
```bash
docker compose exec backend python -m app.data_gen.run --persons 200 --events 800

curl "http://localhost:8000/api/v1/persons?limit=10"
# → JSON array of 10 person objects

curl "http://localhost:8000/api/v1/events?type=call&limit=5"
# → JSON array of 5 call events

docker compose exec backend pytest tests/unit/ -v
# → all tests pass
```

### Definition of Complete
> Running the data gen script with 500+ persons and 2000+ events completes in under 60 seconds, data is queryable via the API with correct pagination, and all unit tests pass.

---

## Phase 3 — Graph Relationships + Anomaly Detection

**Goal**: Relationships are stored in a graph DB and anomalous patterns are detectable.

### Checklist
- [ ] Neo4j running locally via Docker (or AuraDB configured for cloud)
- [ ] `GraphBuilder` writes `(:Person)-[:CONTACTED]->(:Person)` edges for every call/message event
- [ ] `GraphBuilder` writes `(:Person)-[:TRANSACTED]->(:Person)` edges for transfer events
- [ ] `GraphBuilder` writes `(:Person)-[:VISITED]->(:Location)` edges for meeting events
- [ ] `GET /api/v1/graph/neighbourhood/{person_id}?hops=2` returns serialised graph JSON
- [ ] `GET /api/v1/graph/centrality` returns top-10 persons by degree centrality
- [ ] `GET /api/v1/graph/shortest-path?from={id}&to={id}` returns path if it exists
- [ ] `AnomalyService` runs IsolationForest over event frequency data
- [ ] `AnomalyService` applies z-score rule: flag persons with call count > 3σ from mean
- [ ] `POST /api/v1/anomalies/run-detection` triggers detection and saves `AnomalyRecord`s
- [ ] `GET /api/v1/anomalies` returns flagged records with score + reason
- [ ] Anomaly results cached in Redis with 5-minute TTL
- [ ] Integration tests: `pytest tests/integration/test_graph_api.py` → pass
- [ ] Unit tests: `pytest tests/unit/test_anomaly_service.py` → pass

### How to Test Completion
```bash
# After running data gen:
curl "http://localhost:8000/api/v1/graph/neighbourhood/<any-person-id>?hops=2"
# → {"nodes": [...], "edges": [...]}

curl -X POST "http://localhost:8000/api/v1/anomalies/run-detection" \
  -H "Authorization: Bearer <token>"
# → {"flagged": 12, "duration_ms": 340}

curl "http://localhost:8000/api/v1/anomalies?limit=5"
# → JSON array of anomaly records with score + reason fields
```

### Definition of Complete
> Graph neighbourhood queries return correct multi-hop results, anomaly detection flags at least 1 record in a 2000-event dataset, and all integration + unit tests pass.

---

## Phase 4 — Frontend + Backend Integration (Dashboard, Graph, Map)

**Goal**: A complete, visually impressive web dashboard that consumes all backend endpoints.

### Checklist
- [ ] **Dashboard page**: Shows live KPI cards (total persons, events, anomalies), recent events feed
- [ ] **Map page**: Leaflet map renders all fake location pins; clicking a pin shows location detail + events at location
- [ ] **Graph page**: Cytoscape renders neighbourhood graph for a searched person; hop slider works (1–3 hops)
- [ ] **Anomalies page**: Table of flagged records with sortable score column and reason text
- [ ] **Search**: Global search bar queries `/api/v1/persons` and shows results as entity cards
- [ ] **About/Ethics page**: Explains synthetic-data approach, privacy risks of real surveillance
- [ ] **EthicsBanner** component visible at top of every page (not dismissible)
- [ ] Login/register flow works; JWT stored in `localStorage`; expired token redirects to login
- [ ] All API calls use the centralised Axios client from `src/api/client.ts`
- [ ] App is fully responsive (works at 1280px and 768px widths)
- [ ] Loading spinners shown during API fetches; error states handled gracefully
- [ ] Frontend tests: `npm run test` → all pass
- [ ] No `console.error` output in normal usage

### How to Test Completion
```
1. Open http://localhost:5173
2. Register a demo account
3. See KPI cards with non-zero counts on Dashboard
4. Go to Map — see coloured pins scattered across map; click one
5. Go to Graph — search a person's name; graph renders within 3 seconds
6. Go to Anomalies — see at least one flagged record with a score
7. Resize browser to 768px — all pages remain usable
8. Check every page has the ethics banner at the top
```

### Definition of Complete
> A hiring manager can open the app, register, and navigate all four main pages without seeing an error state. The ethics banner is visible on every page. The graph loads within 3 seconds for a 2-hop neighbourhood.

---

## Phase 5 — Optimisation

**Goal**: The app handles 10,000+ persons and 50,000+ events without timing out.

### Checklist
- [ ] PostgreSQL indexes added: `events.occurred_at`, `events.actor_id`, `events.event_type`
- [ ] Full-text search on `persons.full_name` uses GIN index
- [ ] Graph neighbourhood query uses Neo4j index on `Person.id`
- [ ] Redis caching: anomaly results cached (5 min TTL); centrality cached (10 min TTL)
- [ ] Dataset re-generated with 10,000 persons + 50,000 events
- [ ] `GET /api/v1/persons?search=...` responds in < 200ms at 10k persons
- [ ] Graph neighbourhood (2-hop) responds in < 1 second at 10k-node graph
- [ ] Anomaly detection completes in < 30 seconds over 50k events
- [ ] Frontend map renders 1,000 pins without freezing (use marker clustering)
- [ ] Leaflet.js `MarkerClusterGroup` plugin implemented for map clustering
- [ ] Load test: `wrk -t4 -c20 -d30s http://localhost:8000/api/v1/persons` → p99 < 500ms

### Definition of Complete
> All response time targets met on a 10k/50k dataset. Load test shows p99 under 500ms for entity list endpoints. Map loads 1,000 pins with clustering in under 1 second.

---

## Phase 6 — Testing + Hardening

**Goal**: Comprehensive test coverage and no obvious edge-case failures.

### Checklist
- [ ] Backend unit test coverage ≥ 80% (`pytest --cov=app`)
- [ ] Ethics guard unit test: POST body with fake SSN pattern → 400 response ✓
- [ ] Ethics guard unit test: POST body with `_synthetic: true` → passes through ✓
- [ ] Auth tests: expired JWT → 401; missing JWT → 401; wrong password → 401
- [ ] Data gen edge cases: 0 persons, 1 person (no events possible), 1000 persons
- [ ] Graph edge cases: person with no edges, disconnected graph, self-loop prevention
- [ ] Anomaly edge case: no events → detection returns empty list gracefully
- [ ] API pagination: `?limit=0` → 422 validation error; `?limit=1000` → capped at 100
- [ ] Frontend: RTL tests for EthicsBanner, KPICard, AnomalyTable components
- [ ] Run full test suite: `./scripts/run_tests.sh` → all green
- [ ] No hardcoded secrets anywhere (run `trufflehog` scan or `git grep` for patterns)
- [ ] `ruff` linter passes with no errors
- [ ] `eslint` passes with no errors

### Definition of Complete
> `./scripts/run_tests.sh` exits with code 0. Backend coverage ≥ 80%. No hardcoded secrets. Linters clean.

---

## Phase 7 — Deployment

**Goal**: A publicly accessible URL where the demo runs 24/7 on free-tier services.

### Checklist
- [ ] `Dockerfile` builds backend image successfully
- [ ] `frontend/Dockerfile` builds nginx-served React app
- [ ] `docker-compose.prod.yml` created with production overrides
- [ ] Railway project created; PostgreSQL plugin added; backend deployed
- [ ] Vercel project created; frontend deployed from `frontend/` directory
- [ ] `VITE_API_BASE_URL` set in Vercel to the Railway backend URL
- [ ] All backend env vars set in Railway dashboard (no `.env` committed)
- [ ] GitHub Actions `ci.yml`: runs lint + tests on every PR to `dev`
- [ ] GitHub Actions `deploy.yml`: deploys to Railway + Vercel on push to `main`
- [ ] Production URL loads app in browser
- [ ] Production: `GET <RAILWAY_URL>/health` → `{"status": "ok"}`
- [ ] Production: Ethics banner visible
- [ ] Production: Graph, map, anomalies all functional with pre-seeded data

### Definition of Complete
> A public URL is accessible. CI/CD runs automatically on push. A friend can open the URL and use every feature without needing to run anything locally.

---

## Phase 8 — Documentation + Mastery

**Goal**: The project is resume-ready and a stranger can understand every decision.

### Checklist
- [ ] `README.md` includes: project overview, ethics badge, architecture diagram, feature list, local setup, deployment info, tech stack table, screenshots
- [ ] `ETHICS.md` explains: what the project does, what it does NOT do, why privacy matters, risks of real surveillance
- [ ] `PROJECT-MASTERY.md` answers: why each tech was chosen, how anomaly detection works, what tradeoffs were made, what you'd do differently, what you learned
- [ ] FastAPI `/docs` auto-generated OpenAPI spec is clean and has descriptions on all endpoints
- [ ] All API endpoints have docstrings
- [ ] GitHub repo has: description, topics/tags, homepage URL set
- [ ] At least 3 screenshots in `docs/` or embedded in README
- [ ] HANDOFF.md updated to show all phases complete
- [ ] Repo tagged `v1.0.0`

### Definition of Complete
> A hiring manager with no prior context can: (1) read the README in 5 minutes and understand the project, (2) run it locally in under 10 minutes following the README, (3) understand every major technical decision from PROJECT-MASTERY.md. The word "SYNTHETIC" or "FAKE" appears visibly on every page of the running app.

---

*Use this document as your single source of truth for "am I done?"*
