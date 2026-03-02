# SimSight — Complete Folder Structure

> This is the **canonical** directory layout for the entire project.
> Every file has a purpose. Nothing is added without a reason.

```
simsight/                                  ← project root
│
├── .github/                               ← GitHub-specific config
│   ├── workflows/
│   │   ├── ci.yml                         ← lint + test on every PR
│   │   └── deploy.yml                     ← deploy on push to main
│   ├── ISSUE_TEMPLATE/
│   │   └── bug_report.md
│   └── pull_request_template.md
│
├── backend/                               ← Python / FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        ← FastAPI app factory, middleware mount
│   │   ├── config.py                      ← Pydantic settings (reads .env)
│   │   │
│   │   ├── api/                           ← Route handlers (thin controllers)
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                ← /auth/register, /auth/login, /auth/me
│   │   │   │   ├── persons.py             ← /persons CRUD + search
│   │   │   │   ├── locations.py           ← /locations CRUD
│   │   │   │   ├── events.py              ← /events list + filter
│   │   │   │   ├── graph.py               ← /graph/neighbourhood (Redis-cached), /centrality, /path
│   │   │   │   ├── anomalies.py           ← /anomalies list + run-detection (shared Redis pool)
│   │   │   │   └── admin.py               ← /admin/metrics — Phase 5 perf snapshot endpoint
│   │   │   └── deps.py                    ← Shared FastAPI dependencies (get_db, get_current_user)
│   │   │
│   │   ├── models/                        ← SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    ← DeclarativeBase, TimestampMixin
│   │   │   ├── person.py
│   │   │   ├── location.py
│   │   │   ├── event.py
│   │   │   ├── anomaly.py
│   │   │   └── user.py                    ← Auth user model
│   │   │
│   │   ├── schemas/                       ← Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── person.py
│   │   │   ├── location.py
│   │   │   ├── event.py
│   │   │   ├── anomaly.py
│   │   │   ├── graph.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/                      ← Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── entity_service.py          ← Person / Location / Event queries
│   │   │   ├── graph_service.py           ← Neo4j queries, centrality
│   │   │   ├── anomaly_service.py         ← IsolationForest + z-score detection
│   │   │   └── auth_service.py            ← JWT creation + validation
│   │   │
│   │   ├── data_gen/                      ← Synthetic data generation engine
│   │   │   ├── __init__.py
│   │   │   ├── run.py                     ← CLI entry point: python -m app.data_gen.run
│   │   │   ├── person_generator.py        ← Faker-based person factory
│   │   │   ├── location_generator.py      ← Fake lat/lon + building name factory
│   │   │   ├── event_generator.py         ← Fake calls/messages/transfers factory
│   │   │   ├── graph_builder.py           ← Writes edges to Neo4j
│   │   │   └── constants.py               ← Seed config (city centre coords, scales)
│   │   │
│   │   ├── middleware/                    ← FastAPI middleware
│   │   │   ├── __init__.py
│   │   │   ├── ethics_guard.py            ← Rejects any POST body that looks like real PII
│   │   │   ├── timing.py                  ← Phase 5: Request timing, slow-log, X-Response-Time-Ms
│   │   │   └── logging_middleware.py      ← Structured request logging
│   │   │
│   │   └── db/                            ← Database connection management
│   │       ├── __init__.py
│   │       ├── postgres.py                ← SQLAlchemy async engine + session factory
│   │       ├── neo4j.py                   ← Neo4j driver singleton + ensure_neo4j_indexes()
│   │       └── redis.py                   ← Phase 5: Shared Redis pool + CacheHelper fallback
│   │
│   ├── alembic/                           ← Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 0001_initial_schema.py     ← Initial schema + B-tree indexes
│   │       └── 0003_performance_indexes.py ← Phase 5: GIN trigram + anomaly unique constraint
│   │
│   ├── tests/                             ← Pytest test suite
│   │   ├── conftest.py                    ← Fixtures (test DB, test client)
│   │   ├── unit/
│   │   │   ├── test_person_generator.py
│   │   │   ├── test_event_generator.py
│   │   │   ├── test_anomaly_service.py
│   │   │   ├── test_ethics_guard.py
│   │   │   ├── test_performance.py        ← Phase 5: feature matrix speed + dedup logic
│   │   │   ├── test_redis_fallback.py     ← Phase 5: CacheHelper graceful degradation (7 tests)
│   │   │   ├── test_indexes.py            ← Phase 5: static migration 0003 analysis (8 tests)
│   │   │   └── test_timing_middleware.py  ← Phase 5: header, slow log, deque tests (6 tests)
│   │   └── integration/
│   │       ├── test_persons_api.py
│   │       ├── test_graph_api.py
│   │       └── test_auth_api.py
│   │
│   ├── .dockerignore                      ← Phase 5: Excludes tests/caches from prod image
│   ├── Dockerfile                         ← Phase 5: Multi-stage (builder + slim runtime)
│   ├── requirements.txt                   ← Pinned production dependencies
│   ├── requirements-dev.txt               ← Dev + test dependencies
│   └── alembic.ini
│
├── frontend/                              ← React + Vite SPA
│   ├── public/
│   │   ├── favicon.ico
│   │   └── ethics-notice.txt              ← Plain text ethics notice (for crawlers)
│   │
│   ├── src/
│   │   ├── main.tsx                       ← React DOM root
│   │   ├── App.tsx                        ← Router + layout wrapper
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── pages/                         ← One file per route
│   │   │   ├── DashboardPage.tsx          ← KPI cards, recent events
│   │   │   ├── MapPage.tsx                ← Leaflet map with fake pins
│   │   │   ├── GraphPage.tsx              ← Cytoscape relationship graph
│   │   │   ├── AnomaliesPage.tsx          ← Flagged records table
│   │   │   ├── SearchPage.tsx             ← Search + entity detail
│   │   │   └── AboutPage.tsx              ← Ethics explanation page
│   │   │
│   │   ├── components/                    ← Reusable UI components
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx           ← Sidebar + top nav wrapper
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── EthicsBanner.tsx       ← Persistent fake-data warning banner
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   └── RecentEventsFeed.tsx
│   │   │   ├── map/
│   │   │   │   ├── SimMap.tsx             ← Leaflet map wrapper
│   │   │   │   └── LocationPopup.tsx
│   │   │   ├── graph/
│   │   │   │   ├── RelationshipGraph.tsx  ← Cytoscape wrapper
│   │   │   │   └── GraphControls.tsx      ← Hop slider, layout selector
│   │   │   ├── anomalies/
│   │   │   │   └── AnomalyTable.tsx
│   │   │   └── shared/
│   │   │       ├── SearchBar.tsx
│   │   │       ├── EntityCard.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   │
│   │   ├── api/                           ← Axios API client functions
│   │   │   ├── client.ts                  ← Axios instance + interceptors
│   │   │   ├── persons.ts
│   │   │   ├── graph.ts
│   │   │   ├── anomalies.ts
│   │   │   └── admin.ts
│   │   │
│   │   ├── hooks/                         ← Custom React hooks
│   │   │   ├── usePersons.ts
│   │   │   ├── useGraph.ts
│   │   │   ├── useAnomalies.ts
│   │   │   └── useDebounce.ts             ← Phase 5: 300ms debounce for search inputs
│   │   │
│   │   ├── store/                         ← Global state (Zustand)
│   │   │   └── useAppStore.ts
│   │   │
│   │   ├── types/                         ← TypeScript type definitions
│   │   │   ├── person.ts
│   │   │   ├── event.ts
│   │   │   ├── location.ts
│   │   │   ├── graph.ts
│   │   │   └── anomaly.ts
│   │   │
│   │   └── utils/
│   │       ├── formatDate.ts
│   │       ├── colorScale.ts              ← Anomaly score → colour mapping
│   │       └── perf.ts                    ← Phase 5: measureAsync/measureSync/markRender
│   │
│   ├── tests/                             ← Vitest + React Testing Library
│   │   ├── EthicsBanner.test.tsx
│   │   ├── KPICard.test.tsx
│   │   └── SearchBar.test.tsx
│   │
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── .dockerignore                      ← Phase 5: Excludes node_modules/dist from build context
│   ├── nginx.conf                         ← Phase 5: React Router fallback + static caching
│   └── Dockerfile                         ← Phase 5: Multi-stage (Node build + nginx serve)
│
├── docs/                                  ← All project documentation
│   ├── ARCHITECTURE.md                    ← System design doc
│   ├── HANDOFF.md                         ← Phase-by-phase progress tracker
│   ├── FOLDER_STRUCTURE.md                ← This file
│   ├── GIT_BRANCH_STRATEGY.md
│   ├── DEFINITION_OF_DONE.md
│   ├── PHASE-2-EXPLANATION.md             ← Data generation deep dive
│   ├── PHASE-3-EXPLANATION.md             ← Neo4j + anomaly detection
│   ├── PHASE-4-EXPLANATION.md             ← Frontend architecture
│   ├── PHASE-5-EXPLANATION.md             ← Phase 5: benchmarks, Redis keys, debugging guide
│   └── diagrams/
│       └── architecture.excalidraw        ← Visual diagram source
│
├── scripts/                               ← Utility shell scripts
│   ├── seed.sh                            ← Run data generation with defaults
│   ├── reset_db.sh                        ← Wipe + re-migrate + re-seed
│   └── run_tests.sh                       ← Run all tests (backend + frontend)
│
├── .env.example                           ← Template env file (no real secrets)
├── .gitignore
├── docker-compose.yml                     ← Local dev orchestration
├── docker-compose.prod.yml                ← Production overrides
├── README.md                              ← Project overview + quick start
├── ETHICS.md                              ← Standalone ethics statement
└── PROJECT-MASTERY.md                     ← Deep-dive explanation of every decision
```

---

## Key Design Decisions About the Structure

1. **`backend/app/api/` vs `backend/app/services/`** — Routes handle HTTP; services handle logic. This separation makes unit testing possible without spinning up a web server.

2. **`data_gen/` inside `app/`** — The generator imports the same SQLAlchemy models and DB connection as the rest of the app, preventing duplication.

3. **`middleware/ethics_guard.py`** — Ethics enforcement lives in its own clearly-named file so it is never accidentally deleted or bypassed.

4. **`frontend/src/api/`** — All Axios calls centralised here. No component ever calls `fetch()` directly, making it easy to swap the API URL or add auth tokens globally.

5. **`docs/` at root level** — Hiring managers and reviewers see the docs immediately on GitHub.

6. **`scripts/`** — Automation scripts in one folder so the README can simply say "run `./scripts/seed.sh`".
