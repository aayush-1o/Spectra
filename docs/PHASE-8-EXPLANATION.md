# Spectra — Phase 8 Explanation: AI + Risk Intelligence Layer

> ⚠️ **All data in Spectra is 100% synthetic.** No real people are tracked, analysed, or profiled.
> Phase 8 demonstrates AI integration, ML risk modelling, and advanced graph analysis —
> using only computer-generated data.

---

## Overview

Phase 8 transforms Spectra from a data visualisation tool into an **active intelligence platform**.
It adds five capabilities that take the project into Palantir / Recorded Future territory:

1. **Person Risk Scoring** — quantify how "interesting" a synthetic person is
2. **AI-Powered NL Search** — search the database in plain English using Claude
3. **AI Intelligence Summaries** — generate analyst-quality reports per person
4. **Community Detection** — find clusters of connected persons in the graph
5. **Richer Anomaly Detection** — three new ML algorithms on top of the existing two

---

## Task 8.1 — Richer Synthetic Data

### What Changed

Before Phase 8, synthetic persons had basic attributes: name, age, occupation, lat/lon.
Phase 8 enriches every entity to look more like a real intelligence record.

**Person generator additions:**
| Field | Description |
|-------|-------------|
| `fake_phone_primary` | e.g. `+44 7700 900461` |
| `fake_phone_secondary` | Optional second number (50% chance) |
| `fake_email` | `firstname.lastname@fakecorp.net` |
| `fake_nationality` | Drawn from a curated list of 25 nationalities |
| `fake_alias` | Known alias (20% of persons) like `"The Architect"` |
| `risk_category` | Pre-seeded category: `low / medium / high / critical / watch_list` |
| `group_memberships` | 0–3 synthetic org names from `SYNTHETIC_ORGS` |
| `fake_id_number` | `SYN-XXXXXXXX` format |
| `last_seen_lat/lng` | Last known coordinates |

**Event metadata additions:**
| Event Type | New Fields |
|---|---|
| Call | `channel` (voice/video/encrypted), `is_encrypted` (bool) |
| Message | `platform` (Signal/Telegram/WhatsApp/etc.), `content_hash` |
| Transfer | `currency` (USD/EUR/GBP/crypto), `recipient_account` |
| Meeting | `attendee_count`, `is_covert` (bool, 15% of meetings) |

**Location additions:**
- `district` — sub-city area from `DISTRICTS` list
- `threat_level` — weighted: `green` (60%), `amber` (30%), `red` (10%)
- `surveillance_coverage` — bool (50% of locations)

### Why It Matters

The richer data gives the AI features (NL search, AI summaries) significantly more context to work from,
making the intelligence reports look realistic.

---

## Task 8.2 — Person Risk Score

### The Formula

```
risk_score = volume_pts + off_hours_pts + transfer_pts + anomaly_pts  (clamped 0–100)

volume_pts    = 25 × (person_event_count / max_event_count_in_db)
off_hours_pts = 30 × (events_outside_9am_6pm / total_events)
transfer_pts  = 25 × min(max_transfer_usd / 50_000, 1.0)
anomaly_pts   = 20 × min(anomaly_record_count / 10, 1.0)
```

### Design Decisions

- **Volume is relative**: A person with 20 events is only high-risk if most others have 5.
  Using `max_event_count` normalises this.
- **Off-hours is weighted highest** (30 pts) because off-hours activity is the strongest single
  behavioural indicator in real threat intelligence.
- **Transfer cap at $50k**: Above $50k, full points. The ML doesn't gain from distinguishing
  $100k vs $500k for this scoring model.
- **Anomaly cap at 10**: Anomaly flooding (running detection multiple times) shouldn't inflate risk more than a real 10-anomaly person.

### Colour Tiers (RiskBadge)

| Score | Badge | Label |
|-------|-------|-------|
| 0–25 | 🟢 Green | LOW |
| 26–50 | 🟡 Yellow | MEDIUM |
| 51–75 | 🟠 Orange | HIGH |
| 76–100 | 🔴 Red | CRITICAL |

---

## Task 8.6 — Natural Language Search

### Architecture

```
User types: "transfers over $5000 after 10pm in the last month"
    ↓
POST /api/v1/search/nl   { "query": "transfers over $5000 after 10pm" }
    ↓
nl_search_service.parse_nl_query(query)
    ↓  calls Claude claude-sonnet-4-5 with structured system prompt
Claude returns: {"min_transfer_usd": 5000, "after_hour": 22}
    ↓
SQLAlchemy builds query dynamically:
   SELECT DISTINCT persons.*
   JOIN events ON (actor_id = person.id OR target_id = person.id)
   WHERE EXTRACT(hour FROM occurred_at) >= 22
   [post-filter: transfer amount from JSONB metadata]
    ↓
Returns: [PersonResponse, ...]
```

### Supported Filter Fields (what Claude extracts)

| Field | Type | Example |
|-------|------|---------|
| `min_transfer_usd` | number | `5000` |
| `max_transfer_usd` | number | `50000` |
| `after_hour` | int 0-23 | `22` |
| `before_hour` | int 0-23 | `6` |
| `event_type` | string | `"call"` |
| `occupation` | string | `"analyst"` |
| `nationality` | string | `"Arcadian"` |
| `has_alias` | bool | `true` |
| `min_risk_score` | number | `75` |

### Graceful Degradation

If `ANTHROPIC_API_KEY` is not set, `parse_nl_query()` returns `{}` immediately.
The search endpoint then returns all persons (up to 50), unfiltered.
No crash. No error to the user — just an unfiltered result set.

---

## Task 8.7 — AI Intelligence Summaries

### System Prompt Design

Claude is told it is an intelligence analyst summarising synthetic activity patterns.
It receives:
- Person metadata (name, DOB, nationality, alias, risk score, group affiliations)
- Last 20 events in chronological order (with type-specific metadata)
- Anomaly count

It must produce 2–3 paragraphs in formal analytical prose, starting with:
`SUBJECT PROFILE SUMMARY — SYNTHETIC ENTITY [ID]:`

### Example Output

> SUBJECT PROFILE SUMMARY — SYNTHETIC ENTITY 3a91fe2c...:
>
> SUBJECT maintains a notably high volume of encrypted communications, with
> 18 of 23 recorded call events using encrypted channels. Activity patterns suggest
> deliberate avoidance of standard voice channels, concentrated between 22:00 and
> 04:00 UTC...

### Why Claude Sonnet Specifically

- **Speed**: Sonnet is significantly faster than Opus for this text generation task
- **Cost**: ~3–5× cheaper than Opus per token for structured analytical prose
- **Quality**: For this length and structure, Sonnet is indistinguishable from Opus

---

## Task 8.9 — Map Heatmap

### Implementation

The heatmap uses `leaflet.heat` — a Leaflet plugin that renders a canvas layer:

```typescript
L.heatLayer(points, {
    radius: 35,
    blur: 25,
    gradient: { 0.2: '#2563eb', 0.5: '#f59e0b', 0.8: '#ef4444' }
})
```

**Intensity calculation:**
```
intensity = event_count_at_location / max_event_count_across_all_locations
```

This normalises heatmap density so the most-visited location is always at max intensity (red),
and zero-visit locations don't appear on the heatmap at all.

### Pins vs Heatmap

| Mode | Best For |
|------|---------|
| Pins | Inspecting individual locations (click for threat_level, district, events) |
| Heatmap | Identifying activity hotspots across the city at a glance |

---

## Task 8.10 — Community Detection

### Algorithm: Louvain

The Louvain algorithm detects communities by maximising **modularity** — a score that measures
how many edges fall within communities vs between them.

```python
import community as community_louvain
partition = community_louvain.best_partition(G, random_state=42)
# partition = {"person_uuid": community_id, ...}
```

We use `random_state=42` for reproducibility. The same graph will produce the same
community assignments every time (important for the cached result to be consistent).

### Graph Construction

Only `Person → Person` edges are used for community detection:
```cypher
MATCH (a:Person)-[r:CONTACTED|TRANSACTED]->(b:Person)
RETURN a.id AS source, b.id AS target
```

`VISITED` (Person → Location) edges are excluded — location visits don't indicate
social-network community membership.

### Fallback

If `python-louvain` is not installed:
```python
communities_iter = nx.community.greedy_modularity_communities(G)
```
NetworkX's greedy algorithm is slower but always available.

### Caching Strategy

```
Redis key:  graph:communities
TTL:        600s (10 minutes)
```

Community detection on a 200-person graph takes ~50ms. The 10-minute cache means
most requests are served in <1ms from Redis.

### Frontend Rendering

```typescript
// Risk mode: green → yellow → orange → red by risk_score
// Community mode: 12-colour palette by partition ID
const bgColor = colorMode === 'community' && communityId !== undefined
    ? COMMUNITY_PALETTE[communityId % 12]
    : riskColor(n.properties.risk_score)
```

---

## Task 8.11 — New Anomaly Algorithms

### DBSCAN (Density-Based Spatial Clustering)

**Feature space:** `[hour_of_day_sin, hour_of_day_cos, day_of_week, event_type_encoded]`

Events that are **noise points** (not part of any cluster) are labelled anomalies.
These are events that are isolated from the main activity patterns.

```python
db = DBSCAN(eps=0.8, min_samples=5, algorithm='ball_tree')
labels = db.fit_predict(features)
noise_idx = np.where(labels == -1)[0]
```

### LOF (Local Outlier Factor)

LOF detects events whose **local density is much lower** than their neighbours.
It assigns a score — points with scores > 1 are outliers.

```python
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
labels = lof.fit_predict(features)   # -1 = outlier
```

### Night Owl Rule

A deterministic business rule that flags **persons** (not events) with suspicious
concentration of activity during night hours.

```
if count(events between 23:00–04:00) / total_events > 0.60:
    → AnomalyRecord for this person (entity_type="person")
```

This catches synthetic actors whose event cadence is systematically nocturnal —
a simple but interpretable signal that ML-only approaches might miss.

### Algorithm Comparison

| Algorithm | Type | What It Finds | Interpretable? |
|-----------|------|---------------|---------------|
| IsolationForest | Unsupervised ML | Events in sparse feature regions | No |
| Z-score | Statistical | Events with extreme feature values | Yes |
| DBSCAN | Density-based | Events far from any cluster | Partially |
| LOF | Density-based | Events with unusually low local density | Partially |
| Night Owl Rule | Rule-based | Persons with nocturnal activity patterns | **Yes** |

---

## Task 8.12 — Tests

### What's Covered

```
tests/test_phase8.py
├── TestComputeRiskScore (6 tests)
│   ├── test_all_zeros → score = 0.0
│   ├── test_max_score_is_100 → score = 100.0
│   ├── test_mid_score → score = 50.0
│   ├── test_clamped_at_100 → score ≤ 100.0 with absurd inputs
│   ├── test_transfer_cap → $50k+ = full 25 pts
│   └── test_normalisation_by_max_event_count → relative scoring works
├── TestParseNLQuery (4 tests)
│   ├── test_returns_empty_dict_without_api_key → graceful fallback
│   ├── test_claude_response_parsed → JSON correctly extracted
│   ├── test_invalid_json_returns_empty → no crash on bad response
│   └── test_strips_markdown_fences → handles ```json ... ``` wrapping
└── TestAnomalyAlgorithmEnum (4 tests)
    ├── test_dbscan_in_enum
    ├── test_lof_in_enum
    ├── test_night_owl_in_enum
    └── test_all_algorithms_present → complete set check
```

### Testing Philosophy

- **risk_service** is a pure function — deterministic inputs, deterministic outputs — ideal for unit tests
- **nl_search_service** uses real external API calls → **all Claude calls are mocked** via `unittest.mock.patch`. No tokens spent during CI
- **Enum tests** are regression guards — they catch accidental enum value deletions from future migrations

---

## Security Architecture

### API Key Handling

```
User Browser
    │
    ▼  HTTPS
Frontend (Vercel)
    │
    ▼  HTTP (CORS-protected)
Backend API (Render / Docker)
    │
    ├──→ settings.ANTHROPIC_API_KEY ──→ Claude API
    └──→ settings.GOOGLE_API_KEY    ──→ Google APIs
```

**The browser never sees an API key.** All AI calls go through the backend.
The frontend only ever talks to `/api/v1/*` — the backend holds all secrets.

### Environment Variable Resolution

Pydantic-Settings resolves in this order:
1. Real environment variable (cloud platform / Docker env)
2. `.env` file (local dev)
3. Field default (dev fallback, never production)

Production startup (`validate_production()`) will abort if:
- `JWT_SECRET_KEY` is the placeholder value
- `NEO4J_PASSWORD` is a known default (`spectra123`, `password`, `neo4j`)
- `FRONTEND_URL` is not set (would allow any origin in CORS)

---

## File Index (Phase 8 Only)

### New Backend Files
| File | Purpose |
|------|---------|
| `app/services/risk_service.py` | Risk score computation |
| `app/services/nl_search_service.py` | Claude NL query parser |
| `app/services/ai_summary_service.py` | Claude analyst reports |
| `app/services/community_service.py` | Louvain community detection |
| `app/api/v1/search.py` | `POST /api/v1/search/nl` endpoint |
| `alembic/versions/0004_richer_persons.py` | 15 new columns |
| `alembic/versions/0005_anomaly_algorithms.py` | 3 new enum values |
| `tests/test_phase8.py` | 14 unit tests |

### Modified Backend Files
| File | Change |
|------|--------|
| `data_gen/constants.py` | 9 new constant lists |
| `data_gen/person_generator.py` | 8 new fields |
| `data_gen/event_generator.py` | Metadata fields per event type |
| `data_gen/location_generator.py` | 3 new fields |
| `data_gen/graph_builder.py` | Writes risk_score to Neo4j |
| `models/person.py` | 12 new columns |
| `models/location.py` | 3 new columns |
| `models/anomaly.py` | 3 new enum values |
| `services/anomaly_service.py` | DBSCAN, LOF, Night Owl |
| `api/v1/admin.py` | `compute-risk-scores` endpoint |
| `api/v1/persons.py` | `GET /{id}`, `GET /{id}/summary` |
| `api/v1/events.py` | `?person_id=` filter |
| `api/v1/graph.py` | `GET /communities` |
| `schemas/person.py` | New fields |
| `schemas/location.py` | New fields |
| `config.py` | `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, NEO4J guard |
| `main.py` | Register search router, v0.8.0 |
| `requirements.txt` | `anthropic`, `python-louvain` |

### New Frontend Files
| File | Purpose |
|------|---------|
| `components/shared/RiskBadge.tsx` | 4-tier colour badge |
| `components/shared/NLSearchBar.tsx` | AI search bar |
| `components/person/AISummaryPanel.tsx` | Claude report viewer |
| `components/timeline/EntityTimeline.tsx` | Event history timeline |
| `pages/PersonDetailPage.tsx` | Full person profile |

### Modified Frontend Files
| File | Change |
|------|--------|
| `pages/SearchPage.tsx` | Name / AI tab toggle |
| `pages/MapPage.tsx` | Heatmap + pins toggle |
| `pages/GraphPage.tsx` | Uses updated CytoscapeGraph |
| `components/graph/CytoscapeGraph.tsx` | Risk + community coloring |
| `App.tsx` | `/person/:id` route added |
| `api/persons.ts` | `getPersonById`, `getPersonSummary`, `nlSearch` |
| `api/events.ts` | `person_id` filter param |
| `types/index.ts` | Updated Person, Location, new types |
| `package.json` | `leaflet.heat` added |
