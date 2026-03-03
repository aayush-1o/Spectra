# Phase 7 — Deployment Explanation

This document explains every decision made in Phase 7, the production
deployment of Spectra.

---

## 1. Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB                                   │
│                                                                 │
│  dev branch  ──PR──►  CI pipeline (ci.yml)                      │
│                        ├── Backend tests (Pytest, real PG)     │
│                        ├── Frontend tests (Vitest)             │
│                        └── Lint (Ruff + ESLint)                │
│                                                                 │
│  main branch ──push──► Deploy pipeline (deploy.yml)             │
│                         ├── Re-run unit tests                  │
│                         ├── Trigger Render deploy hook         │
│                         └── Vercel CLI --prod                  │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────────┐
            │                      │                          │
            ▼                      ▼                          ▼
┌───────────────────┐   ┌─────────────────────┐   ┌──────────────────┐
│   Render          │   │   Vercel CDN         │   │  Managed DBs     │
│   (Backend)       │   │   (Frontend)         │   │                  │
│                   │   │                      │   │  Render Postgres │
│  FastAPI 0.7.0    │◄──┤  React 18 SPA        │   │  (primary store) │
│  Uvicorn 2 workers│   │  Code-split pages    │   │                  │
│  Port: $PORT      │   │  nginx + CDN         │   │  Upstash Redis   │
│  /health + /ready │   │  HTTPS auto          │   │  (cache, TLS)    │
│  Alembic migrate  │   │  vercel.json rewrites│   │                  │
│  on every deploy  │   │                      │   │  Neo4j AuraDB    │
└───────┬───────────┘   └─────────────────────┘   │  (graph DB)      │
        │                                          └──────────────────┘
        └────────────── connects to all 3 DBs ─────────────────────────┘
```

---

## 2. Platform Choices & Justification

| Service | Platform | Reason |
|---------|----------|--------|
| Backend | **Render** | Native Docker support, Blueprint spec (`render.yaml`), free PostgreSQL add-on, auto-deploy on push, `$PORT` injection, health-check-based rolling deploys |
| Frontend | **Vercel** | Zero-config Vite support, instant global CDN, free SSL, GitHub integration, SPA rewrite rules via `vercel.json` |
| PostgreSQL | **Render Postgres** | Same datacenter as backend (low latency), managed backups, internal network connection (no SSL overhead) |
| Redis | **Upstash** | Serverless pricing (pay per command), supports `rediss://` TLS, no connection pool limits on free tier, REST API as fallback |
| Neo4j | **AuraDB Free** | Fully managed, 200MB free, Bolt+TLS (`neo4j+s://`), no infra needed, same driver as local dev |
| CI/CD | **GitHub Actions** | Free for public repos, Docker service containers (real Postgres/Redis in CI), tight GitHub integration |

### Why not Railway?
Railway doesn't support Blueprint-style declarative infra as cleanly and charges
for PostgreSQL immediately. Render's free PostgreSQL + Blueprint inspec is better for portfolio projects.

### Why not Netlify?
Both work for React/Vite. Vercel has better Vite auto-detection and faster
build times, and its `vercel.json` rewrite syntax is more straightforward.

---

## 3. Environment Variable Separation Strategy

```
.env              ← dev defaults (gitignored)
.env.example      ← committed: documents all vars with dev values
backend/.env.production.example ← committed: cloud format examples (no real values)
```

In code, `settings.environment` controls behaviour:

| Flag | Dev | Production |
|------|-----|-----------|
| `allow_docs` | `True` (shows /docs, /redoc) | `False` (returns 404) |
| `debug` | `False` (can set True locally) | `False` (always) |
| `log_level` | `INFO` | `INFO` (ERROR surfaces in dashboards) |
| `cors_origins` | localhost:5173, localhost:3000 | FRONTEND_URL only |
| DB echo | Off | Off |
| JWT validation | Warns if default | **Crashes startup** if default |

---

## 4. CI/CD Explanation

### ci.yml — runs on PR to dev or main
```
PR opened
  │
  ├── backend-test
  │     ├── Spin up Postgres + Redis (Docker service containers)
  │     ├── pip install -r requirements.txt
  │     ├── ruff check (lint)
  │     └── pytest tests/unit/ -v
  │
  └── frontend-test
        ├── npm ci
        ├── eslint src/
        └── npm run test (Vitest)
```

### deploy.yml — runs on push to main (merge from dev)
```
Commit pushed to main
  │
  ├── test (same as ci.yml backend job — gates deploy)
  │
  ├── deploy-backend
  │     ├── curl RENDER_DEPLOY_HOOK_URL
  │     └── Poll /health every 10s for 3 minutes
  │
  └── deploy-frontend
        ├── npm install -g vercel
        └── vercel --prod (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)
```

**Gate:** `deploy-backend` and `deploy-frontend` both depend on `test` succeeding.
If tests fail, nothing deploys.

---

## 5. Health Checks Explanation

### `GET /health` — Liveness Probe
Checks all three backing services (Postgres, Redis, Neo4j) with real I/O:
- Postgres: `SELECT 1`
- Redis: `PING`
- Neo4j: `RETURN 1`

Returns 200 even if a service is degraded (for liveness decisions).
Returns `"status": "degraded"` if any sub-check fails.

Used by: Render (container restart decision), CI health poll.

### `GET /ready` — Readiness Probe
Same checks as `/health`, but returns **503** if any service is unreachable.

Used by: Load balancers, smoke tests after deploy, manual validation.

```bash
# Validate production is fully ready
curl -f https://<your-render-url>/ready
# exit 0 if all services up, exit 22 if 503
```

---

## 6. Production Logging Explanation

### StructuredLoggingMiddleware

Every request emits one log line. In production it's JSON:

```json
{
  "timestamp": "2026-03-02T13:00:00.000Z",
  "method": "GET",
  "path": "/api/v1/persons",
  "status_code": 200,
  "duration_ms": 42.3,
  "client_ip": "1.2.3.4",
  "environment": "production"
}
```

5xx responses include `"error": "<exception message>"`.

Health probe paths (`/health`, `/ready`) are logged at DEBUG to avoid noise.

Render's log aggregator parses JSON lines — you can filter by `status_code`, `path`, etc.

### TimingMiddleware (Phase 5, still active)
- Adds `X-Response-Time-Ms` header to every response
- Logs WARNING for requests > 200ms
- Maintains rolling 1000-sample average accessible via `GET /api/v1/admin/metrics`

---

## 7. Security Checklist

| Check | Implementation |
|-------|---------------|
| HTTPS enforced | Render + Vercel provide HTTPS by default; mixed content blocked |
| JWT secret validated | `validate_production()` crashes startup if key is default |
| No wildcard CORS | `cors_origins` in prod reads `FRONTEND_URL` or `CORS_ORIGINS_OVERRIDE` only |
| /docs disabled in prod | `allow_docs=False` → FastAPI returns 404 for /docs and /redoc |
| No secrets in Git | `.env` is gitignored; `.env.example` has no real values |
| SQL injection | SQLAlchemy ORM + parameterised queries throughout |
| Password hashing | bcrypt (work factor 12) via passlib |
| Ethics guard | Rejects any request body matching real PII patterns |

---

## 8. Known Production Risks

| Risk | Mitigation |
|------|-----------|
| Render free tier spins down | First request after idle takes ~30s. Use UptimeRobot free ping to keep awake |
| AuraDB 200MB limit | With current data scale (~5,000 persons) usage is well within limits |
| Upstash 10k cmd/day limit | Each page load uses ~2-4 Redis commands. 10k covers ~2500 page loads/day |
| Render free Postgres 90-day expiry | Databases expire after 90 days on free tier — upgrade or migrate before expiry |
| Cold-start Neo4j connection | `ensure_neo4j_indexes()` is non-fatal; system degrades gracefully |
| JWT secret rotation invalidates sessions | Document and communicate before rotating; users must re-login |

---

## 9. Rollback Strategy

### Code rollback
```bash
# Revert the bad commit and push to main
git revert HEAD
git push origin main
# → deploy.yml triggers automatically
```

### Render UI rollback
Render → Deploys → click any past deploy → **Redeploy**

### Database rollback
Alembic supports downgrade, but use carefully:
```bash
# Inside Render shell or via one-off job
alembic downgrade -1   # revert one migration
```

> ⚠️ Downgrading the 0003 migration drops the GIN index and unique constraint.
> Anomaly deduplication will stop working until the migration is re-applied.

---

## 10. Production URLs

The project is **not currently hosted**. URLs below are placeholders for when deployment is configured.

| Service | Placeholder URL |
|---------|----------------|
| Backend API | `https://<your-render-url>` |
| Frontend | `https://<your-vercel-url>` |
| API Docs | Disabled in production (`ALLOW_DOCS=false`) |
| Health | `https://<your-render-url>/health` |
| Ready | `https://<your-render-url>/ready` |

---

## Future Improvements

- **Sentry integration** — structured error tracking with stack traces
- **UptimeRobot** — free external uptime monitoring (ping /health every 5 min)
- **Docker Hub / GHCR** — push image to registry for faster Render deploys
- **Staging environment** — separate Render service pointing to dev branch
- **Database connection pooling** — PgBouncer or Render's built-in pooler for high load
- **Materialized views** — for KPI dashboard aggregations (Phase 5 roadmap)
