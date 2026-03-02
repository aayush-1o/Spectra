# Spectra — Deployment Guide (Phase 7)

> All data is 100% synthetic. No real surveillance.

This is the step-by-step manual deployment guide for getting Spectra
running publicly on Render (backend) + Vercel (frontend).

---

## Prerequisites

- GitHub account (repo already exists)
- [Render](https://render.com) account (free)
- [Vercel](https://vercel.com) account (free)
- [Upstash](https://upstash.com) account (free)
- [Neo4j AuraDB](https://neo4j.com/cloud/platform/aura-graph-database/) account (free)
- Node.js 20+ locally (for Vercel CLI)

---

## 1. Set Up Neo4j AuraDB (Free)

1. Go to [console.neo4j.io](https://console.neo4j.io)
2. Click **New instance** → **AuraDB Free**
3. Note the generated `NEO4J_URI` (format: `neo4j+s://xxxx.databases.neo4j.io`)
4. Download the credentials file (you only see the password once)
5. Save: `NEO4J_URI`, `NEO4J_USERNAME` (= `neo4j`), `NEO4J_PASSWORD`

---

## 2. Set Up Upstash Redis (Free)

1. Go to [console.upstash.com](https://console.upstash.com)
2. Click **Create Database** → region closest to your Render service
3. Under **Details**, find **Redis URL** (starts with `rediss://`)
4. Save: `REDIS_URL`

---

## 3. Deploy Backend to Render

### Option A: Blueprint (recommended — one click)

1. Go to [render.com/deploy](https://render.com)
2. Click **New → Blueprint**
3. Connect your GitHub repo → Render finds `render.yaml` automatically
4. Render creates `spectra-api` (web service) + `spectra-postgres` (database)
5. In the service **Environment** tab, add these secret env vars manually:
   ```
   JWT_SECRET_KEY     = <run: python -c "import secrets; print(secrets.token_hex(32))">
   NEO4J_URI          = neo4j+s://xxxx.databases.neo4j.io
   NEO4J_USERNAME     = neo4j
   NEO4J_PASSWORD     = <from AuraDB>
   REDIS_URL          = rediss://default:xxxx@xxxx.upstash.io:6379
   FRONTEND_URL       = https://spectra-simsight.vercel.app  (update after Vercel step)
   ```
6. Click **Deploy** — Render runs migrations then starts the server

### Option B: Manual service

1. New → **Web Service** → Docker → connect repo
2. Root directory: `backend`
3. Dockerfile path: `./Dockerfile`
4. Start command: `sh scripts/migrate_and_start.sh`
5. Add same env vars as above
6. **Health check path**: `/health`

### Verify backend is live

```bash
curl https://spectra-api.onrender.com/health
# → {"status":"ok","project":"Spectra","version":"0.7.0",...}

curl https://spectra-api.onrender.com/ready
# → {"ready":true,"services":{...}}
```

> ⚠️ **Free tier note**: Render free services spin down after 15 min of inactivity.
> First request after spin-down takes ~30s. Upgrade to Starter ($7/mo) for always-on.

---

## 4. Deploy Frontend to Vercel

### Option A: Vercel Dashboard (recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. **Framework preset**: Vite
4. **Root directory**: `frontend`
5. **Environment variables** (in Vercel dashboard):
   ```
   VITE_API_BASE_URL = https://spectra-api.onrender.com
   ```
6. Click **Deploy**
7. Note your Vercel URL (e.g. `https://spectra-simsight.vercel.app`)

### Option B: Vercel CLI

```bash
npm install -g vercel
cd frontend
vercel login
vercel link          # creates .vercel/project.json
vercel env add VITE_API_BASE_URL  # enter: https://spectra-api.onrender.com
vercel --prod
```

### Set FRONTEND_URL on Render

After you have the Vercel URL, go back to Render:
```
FRONTEND_URL = https://spectra-simsight.vercel.app
```
Then **redeploy** the Render service so CORS allows the frontend.

---

## 5. Configure GitHub Actions (CI/CD)

### CI (already works — no secrets needed)
The `ci.yml` workflow runs automatically on every PR to `dev` or `main`.

### Deploy (requires secrets)
Go to **GitHub repo → Settings → Secrets → Actions → New repository secret**:

| Secret | Where to get it |
|--------|----------------|
| `RENDER_DEPLOY_HOOK_URL` | Render service → Settings → Deploy Hooks → Create |
| `VERCEL_TOKEN` | vercel.com/account/tokens → Create |
| `VERCEL_ORG_ID` | Run `vercel link` → check `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | Same file as above |

Also add a **repository variable** (not secret):
| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://spectra-api.onrender.com` |

---

## 6. Run Alembic Migrations in Production

Migrations run automatically on every deploy via `migrate_and_start.sh`.

To run manually:
```bash
# Via Render shell (service → Shell tab)
alembic upgrade head

# Or via the Render one-off job (if configured)
# Or by triggering a new deploy
```

---

## 7. Generate Synthetic Data in Production

After the backend is live:
```bash
# Via Render shell
python -m app.data_gen.run --persons 200 --events 800
python -m app.data_gen.graph_builder
```

---

## 8. Rotate JWT Secret

1. Generate new key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update `JWT_SECRET_KEY` in Render environment
3. Redeploy the service
4. **All existing tokens are immediately invalidated** — users must log in again

---

## 9. Inspect Production Logs

```bash
# Render dashboard → your service → Logs
# Or via Render CLI:
render logs --tail spectra-api
```

Look for:
- `status_code: 5xx` → server errors
- `"slow": true` → requests over 200ms
- `duration_ms > 1000` → very slow queries

---

## 10. Restart Service Safely

```bash
# Render dashboard → Manual Deploy → Deploy latest commit
# Or via deploy hook:
curl -X POST "$RENDER_DEPLOY_HOOK_URL"
```

Render performs a **rolling restart**: new container starts, passes health check, then old one is stopped. Zero downtime.

---

## 11. Rollback

1. Go to Render → **Deploys** tab
2. Find the last known-good deploy
3. Click **Rollback to this deploy**

Or via git:
```bash
git revert HEAD
git push origin main
# → triggers new deploy automatically
```
