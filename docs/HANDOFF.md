# Spectra — Session Handoff Document

> Last updated: Phase 10 complete.

---

## Current Phase

**Phase**: 10 — CesiumJS 3D Globe Intelligence Platform ✅ **COMPLETE**

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
| 8 | AI + Risk Intelligence Layer | ✅ Complete |
| 9 | Real-Time Asset Tracking (WebSocket) | ✅ Complete |
| **10** | **CesiumJS 3D Globe Intelligence Platform** | ✅ **Complete** |

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

### Phase 2 — Data Engine
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

#### 8.1 Richer Data Fields
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
- [x] `frontend/src/components/shared/NLSearchBar.tsx` — NL search bar with result cards
- [x] `frontend/src/pages/SearchPage.tsx` — Name / AI Search tab toggle

#### 8.9 Map Heatmap
- [x] `leaflet.heat` installed
- [x] `frontend/src/pages/MapPage.tsx` — Pins/Heatmap toggle

#### 8.10 Graph Community + Risk Coloring
- [x] `backend/app/services/community_service.py` — Louvain detection + networkx fallback, Redis cache 600s
- [x] `backend/app/api/v1/graph.py` — `GET /api/v1/graph/communities`
- [x] `frontend/src/components/graph/CytoscapeGraph.tsx` — Risk mode (green→red) + Community mode (12-colour palette)

#### 8.11 Richer Anomaly Detection
- [x] `backend/app/services/anomaly_service.py` — DBSCAN, LOF, Night Owl Rule (>60% night events)
- [x] `backend/app/models/anomaly.py` — `dbscan`, `lof`, `night_owl_rule` added to AnomalyAlgorithm enum
- [x] `backend/alembic/versions/0005_anomaly_algorithms.py` — `ALTER TYPE ... ADD VALUE IF NOT EXISTS`

---

### Phase 9 — Real-Time Asset Tracking ✅

#### 9.1 Synthetic Telemetry Generator
- [x] `backend/app/data_gen/synthetic_telemetry.py` — `TelemetryGenerator`, `Asset`, `AssetPosition` dataclasses; haversine distance + waypoint interpolation
- [x] Three asset types: `DRONE` (50-300 m), `FLIGHT` (5,000-12,000 m), `VEHICLE` (0 m)
- [x] Fleet of 60 assets spread globally with per-type speed ranges, alias-based callsigns, looping waypoint circuits
- [x] Module-level `get_fleet()` singleton so all WebSocket connections share the same moving fleet

#### 9.2 WebSocket Stream Endpoint
- [x] `backend/app/api/v1/stream.py` — `ConnectionManager` + `WS /api/v1/stream/assets`
- [x] On-connect manifest frame (`{type: "manifest", assets: [...]}`)
- [x] 1 Hz position broadcast (`{type: "positions", data: [...]}`)
- [x] `GET /api/v1/stream/assets/snapshot` — REST fallback for initial render
- [x] Registered in `backend/app/main.py` at `/api/v1/stream`, version bumped to `0.9.0`

#### 9.3 Frontend: Types + Hook
- [x] `frontend/src/types/telemetry.ts` — `AssetPosition`, `AssetManifest`, `TelemetryFrame`, `HistoryEntry`
- [x] `frontend/src/hooks/useAssetStream.ts` — WS lifecycle, exponential back-off (1s → 30s), rolling 120s history buffer

#### 9.4 Frontend: TimeScrubber
- [x] `frontend/src/components/map/TimeScrubber.tsx` — play/pause, speed 1x/2x/5x, slider, LIVE button

#### 9.5 Frontend: AssetTrackingPage (v1 — Deck.gl)
- [x] `frontend/src/pages/AssetTrackingPage.tsx` — Deck.gl + MapLibre GL flat map
- [x] `IconLayer`, `PathLayer`, `TextLayer`

#### 9.6 Routing + Nav
- [x] `/live-map` route added to `frontend/src/App.tsx`
- [x] Live Tracking nav link added to `frontend/src/components/layout/Sidebar.tsx`

#### 9.7 Tests
- [x] `backend/tests/test_phase9.py` — 18 unit tests

---

### Phase 10 — CesiumJS 3D Globe Intelligence Platform ✅

#### 10.1 Dependencies Installed
- [x] `npm install resium cesium vite-plugin-static-copy` (49 packages)
- [x] Zero vulnerabilities

#### 10.2 Vite Configuration Updated
- [x] `frontend/vite.config.ts` — `vite-plugin-static-copy` copies Cesium's `Workers/ThirdParty/Assets/Widgets` to `/public/cesium/`
- [x] `define: { CESIUM_BASE_URL: '"/cesium"' }` — tells Cesium runtime where to load web workers from
- [x] ESM-compatible (uses `import.meta.url` + `fileURLToPath`, not `require.resolve`)

#### 10.3 HTML Updated
- [x] `frontend/index.html` — added JetBrains Mono + Inter from Google Fonts, Cesium widgets CSS

#### 10.4 Environment
- [x] `frontend/.env` — added `VITE_CESIUM_TOKEN` (Cesium Ion Default Token)

#### 10.5 AssetTrackingPage — Full Replacement
- [x] `frontend/src/pages/AssetTrackingPage.tsx` — replaced Deck.gl with Resium/CesiumJS 3D globe
- [x] `Cesium.Ion.defaultAccessToken` set from `VITE_CESIUM_TOKEN` env var
- [x] `<BillboardCollection>` — assets at 3D positions with altitude-awareness
  - Flights: `max(altitude_m, 3000)`, HeightReference.NONE
  - Drones: `max(altitude_m, 50)`, HeightReference.NONE
  - Vehicles: HeightReference.CLAMP_TO_GROUND
- [x] `<PolylineCollection>` — ghost trails using `PolylineGlowMaterialProperty`
- [x] SVG billboard icons (blue=flights, purple=drones, green=vehicles) — inline SVG data URIs

#### 10.6 HUD Overlay (HTML above Cesium canvas)
- [x] Red classification banner — `TS // SI-TK // NOFORN — SYNTHETIC DATA ONLY`
- [x] Top-left: SPECTRA logo + connection status pill
- [x] Top-left: Asset type count badges (flights / drones / vehicles)
- [x] Top-right: UTC Zulu clock (ticking every second)
- [x] Top-right: Cursor lat/lon readout (live cursor tracking on globe)
- [x] Top-right: Visual mode toggles (Normal / Night Vision / Thermal / Tactical)
- [x] Left panel: scrollable asset list — monospace 12px, color-coded, speed + altitude per row
- [x] Right panel: selected asset detail card (click to open) — LAT/LON/ALT/HEADING/SPEED
- [x] Bottom: existing `<TimeScrubber>` — zero changes

#### 10.7 Visual Mode Toggles
- [x] **Normal** — no filter
- [x] **Night Vision** — CSS `brightness(0.65) hue-rotate(88deg) saturate(4) sepia(0.55)` + scanline overlay
- [x] **Thermal** — CSS `brightness(0.8) sepia(1) saturate(6) hue-rotate(-28deg)` — orange/red
- [x] **Tactical** — CSS `brightness(0.45) saturate(0.15) contrast(1.5)` + CSS grid overlay (green 60px grid)
- [x] All 4 modes are pure CSS `filter` — no real sensor data, no paid APIs

#### 10.8 Typography
- [x] JetBrains Mono for all telemetry coordinates and IDs
- [x] Minimum 12px for data rows, 14-18px for labels
- [x] Deep navy `#050810` dark tactical background
- [x] High-contrast: `#e2e8f0` (near-white) on dark backgrounds

#### 10.9 Unchanged Files
- [x] `frontend/src/hooks/useAssetStream.ts` — zero changes
- [x] `frontend/src/components/map/TimeScrubber.tsx` — zero changes
- [x] `frontend/src/types/telemetry.ts` — zero changes
- [x] All backend files — zero changes

#### 10.10 Documentation
- [x] `docs/PHASE-10-EXPLANATION.md` — architecture diagram, visual mode table, altitude table, Vite config explanation, debugging guide
- [x] `docs/HANDOFF.md` — Phase 10 section (this file)
- [x] `README.md` — Phase 10 badge, CesiumJS in tech stack, 3 new feature rows, VITE_CESIUM_TOKEN in env table

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
| `VITE_CESIUM_TOKEN` | ✅ **Globe** | **Cesium Ion satellite imagery token** |

---

## Deployment

The project is not currently hosted. It runs fully via Docker Compose locally.
See `docs/DEPLOYMENT.md` for instructions on deploying to Render + Vercel.

---

## How To Run Phase 10 (Fresh Start)

```bash
# 1. Full rebuild
docker compose up --build -d

# 2. Run all migrations
docker exec spectra-backend alembic upgrade head

# 3. Seed data (5,000 persons, 50,000 events)
docker exec spectra-backend python -m app.data_gen.run --persons 5000 --events 50000

# 4. Build Neo4j graph
docker exec spectra-backend python -m app.data_gen.graph_builder

# 5. Install/verify frontend dependencies (cesium + resium)
cd frontend && npm install

# 6. Start dev server
npm run dev
# Verify: "[vite-plugin-static-copy] Collected 383 items." appears in output

# 7. Open the 3D Globe
open http://localhost:5173/live-map

# 8. Verify WebSocket feed
curl http://localhost:8000/api/v1/stream/assets/snapshot | python3 -m json.tool
```

---

## Known Nuances + Design Decisions

| # | Description | Area | Severity |
|---|-------------|------|----------|
| 1 | Pyre2 shows "Cannot find import" for all `app.*` — it doesn't have Docker's Python path. Safe to ignore. | All files | Info |
| 2 | `transfer_amount` filtering in NL search is done Python-side (not SQL) because `metadata_` is JSONB. Max 50 results. | `search.py` | Low |
| 3 | Louvain community detection uses `random_state=42` for reproducibility, but results are cached 600s anyway. | `community_service.py` | Low |
| 4 | `graph_builder.py` uses `async for ... break` pattern to get a single session from the async generator. | `graph_builder.py` | Low |
| 5 | `ANTHROPIC_API_KEY` absent → graceful degradation: NL search returns empty filters, AI summary returns a placeholder string. No crash. | AI services | Info |
| 6 | Night Owl Rule anomaly records are person-level (entity_type = "person"), not event-level. | `anomaly_service.py` | Low |
| 7 | CesiumJS without `VITE_CESIUM_TOKEN` renders a solid-colour globe (no satellite imagery). App does not crash. | `AssetTrackingPage.tsx` | Info |
| 8 | `vite-plugin-static-copy` copies 383 Cesium files on every dev server start — startup takes ~1-2s extra. | `vite.config.ts` | Low |
| 9 | `PolylineGlowMaterialProperty` is not a `Material` — cast as `unknown as Cesium.Material` to satisfy Resium's type. Renders correctly at runtime. | `AssetTrackingPage.tsx` | Low |
| 10 | Visual mode filters are CSS `filter` applied to the Cesium canvas wrapper div. Cesium's internal rendering is unchanged. | `AssetTrackingPage.tsx` | Info |

---

*Update this file at the end of each session.*
