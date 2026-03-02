# PHASE-1-EXPLANATION.md — Spectra Phase 1 Deep Dive

> This document explains **everything** built in Phase 1 — what each file does,
> why it was built that way, how the pieces connect, and what you should be able
> to explain in an interview.
>
> Read this before starting Phase 2. Do not skip it.

---

## What Phase 1 Actually Built

Phase 1 is the **skeleton** of the entire application. Nothing user-visible was built.
What was built is the invisible infrastructure that everything else sits on:

- A containerised local environment (Docker)
- A relational database with a defined schema (PostgreSQL + SQLAlchemy + Alembic)
- A working API server with one real feature: authentication (FastAPI + JWT)
- A safety layer that prevents real data from ever entering the system (Ethics Guard)
- A frontend that loads in a browser and shows the ethics banner (React + Vite)

Think of Phase 1 as pouring the foundation of a building. You can't live in it yet,
but without it, nothing else can be built safely.

---

## Part 1 — Docker and the Local Environment

### File: `docker-compose.yml`

This file defines three services that run together:

**spectra-postgres** — the PostgreSQL database.
- Uses the official `postgres:15-alpine` image (small footprint)
- Creates a database called `spectra` with username/password both `spectra`
- Data persists in a Docker volume (`postgres_data`) so it survives container restarts
- Has a healthcheck: `pg_isready` pings the DB every 10 seconds. The backend won't start until this passes

**spectra-redis** — the Redis cache.
- Uses `redis:7-alpine`
- Not used in Phase 1 at all, but wired up now so it's ready for Phase 3 (caching anomaly results)
- Healthcheck: `redis-cli ping`

**spectra-backend** — the FastAPI application.
- Built from `./backend/Dockerfile`
- Waits for both postgres and redis to be healthy before starting (the `depends_on` + `condition: service_healthy` block)
- Mounts `./backend:/app` as a volume — this is why `--reload` works: code changes on your disk are immediately visible inside the container
- Passes environment variables from the host (your `.env` file) into the container

**Why Docker?** Reproducibility. Anyone who clones this repo gets the exact same environment regardless of their OS or what's installed locally. "Works on my machine" is eliminated.

**Why healthchecks?** Without them, the backend might start before PostgreSQL is ready to accept connections, causing a crash-on-startup. The healthcheck ensures the dependency is genuinely ready, not just "running".

---

## Part 2 — The Backend Dockerfile

### File: `backend/Dockerfile`

```
FROM python:3.11-slim
WORKDIR /app
RUN apt-get install gcc libpq-dev   ← needed to compile asyncpg and bcrypt C extensions
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", ...]
```

**Why python:3.11-slim?** The `-slim` variant has fewer pre-installed packages, making the image smaller and faster to build. We install only what we need (`gcc`, `libpq-dev`).

**Why `gcc` and `libpq-dev`?** The `asyncpg` database driver and `bcrypt` hashing library both have C extensions that need to be compiled during `pip install`. Without `gcc`, the build fails.

**Why copy `requirements.txt` separately before copying the full app?** Docker caches each layer. If you copy everything at once and then change a `.py` file, Docker must re-run `pip install`. By copying `requirements.txt` first and running `pip install` as a separate layer, Docker can reuse the cached pip layer as long as `requirements.txt` hasn't changed. This makes rebuilds 10x faster during development.

---

## Part 3 — Configuration

### File: `backend/app/config.py`

```python
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://..."
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    ...
```

`pydantic-settings` reads environment variables automatically. The variable names in the class map directly to environment variable names (case-insensitive). So if `JWT_SECRET_KEY` is set in your `.env` file or in Docker's environment block, Pydantic reads it automatically.

**Why `@lru_cache` on `get_settings()`?**
Without caching, every request to the API would re-read the `.env` file and re-create the Settings object. `@lru_cache` ensures this only happens once at startup, then the same object is reused. This is the standard FastAPI pattern for settings.

**The `cors_origins` property** returns a list of allowed frontend URLs. In development, that's `localhost:5173` (Vite default). The property is computed dynamically so you can add production URLs by just setting `ENVIRONMENT=production` in your env.

---

## Part 4 — The Database Layer

### File: `backend/app/db/postgres.py`

This file sets up the async database connection.

```python
engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,  # logs SQL in dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

**Why async?** FastAPI is built on async Python (ASGI). Using a synchronous DB driver would block the event loop every time a query runs, destroying the performance benefits of async. `asyncpg` is the async PostgreSQL driver; `create_async_engine` wraps it.

**What is connection pooling?** Opening a new database connection for every request is expensive (~50ms per connection). A pool keeps N connections open and reuses them. `pool_size=10` means up to 10 simultaneous connections. `max_overflow=20` allows bursting to 30 under heavy load.

**`pool_pre_ping=True`** — before giving you a connection from the pool, SQLAlchemy sends a `SELECT 1` ping to verify the connection is still alive. Prevents "stale connection" errors after the DB restarts.

**`get_async_session()` generator:**
```python
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

This is a Python async generator used as a FastAPI dependency. The `yield` hands the session to the route handler. After the handler finishes:
- If no exception: `commit()` saves any pending changes
- If exception: `rollback()` undoes them
- Always: `close()` returns the connection to the pool

This pattern ensures you never accidentally leave uncommitted transactions open.

---

## Part 5 — The Data Models

### Files: `backend/app/models/`

All models inherit from three building blocks defined in `base.py`:

**`Base`** — SQLAlchemy's `DeclarativeBase`. Every model that inherits from this is automatically registered with Alembic and can be auto-detected for migrations.

**`TimestampMixin`** — adds `created_at` and `updated_at` columns to any model. The `default=lambda: datetime.now(timezone.utc)` uses a callable so the timestamp is generated fresh for each new row, not captured once at class definition time. `onupdate` does the same for updates.

**`UUIDMixin`** — adds a UUID primary key. UUIDs are better than auto-increment integers for distributed systems because two different servers can both create a new row without coordinating — their IDs won't collide.

### Why `metadata_` not `metadata`?

In every model with a JSON column, the Python attribute is named `metadata_` but maps to the DB column `"metadata"`:

```python
metadata_: Mapped[dict] = mapped_column("metadata", JSON, ...)
```

SQLAlchemy's `DeclarativeBase` has a built-in attribute called `metadata` (it stores table definitions). If you name your column `metadata`, Python gets confused about which `metadata` you mean. The trailing underscore is a Python convention for "this name would conflict with a built-in, so I'm escaping it".

### The `_synthetic: true` default

Every JSON column has this default:
```python
default=lambda: {"_synthetic": True}
```

This means every record generated by the data engine will carry proof that it's synthetic. The ethics guard middleware checks incoming data; this watermark marks stored data. Two-pronged approach.

### Relationships

The models define SQLAlchemy relationships so you can do things like `event.actor.fake_name` without writing a JOIN manually. The `lazy="select"` parameter means relationships are loaded on-demand (a separate SELECT query when you access them), not eagerly loaded by default. This prevents accidentally fetching thousands of related records when you just wanted the parent.

---

## Part 6 — Alembic: Database Migrations

### Files: `backend/alembic/`

Alembic is a database migration tool. It lets you evolve your schema over time without manually writing `ALTER TABLE` SQL.

**Why not just `Base.metadata.create_all()`?**
`create_all()` only works for the initial creation. If you want to add a column to an existing table in production, it won't help. Alembic generates versioned migration files that can be applied (upgrade) or reversed (downgrade).

**`alembic/env.py`** is the engine configuration for Alembic. The critical part is:
```python
from app.models import *  # import all models so Alembic can "see" them
target_metadata = Base.metadata
```
Without importing the models, Alembic has nothing to compare your database against and won't generate correct migrations.

**`asyncio.run(run_migrations_online())`** — because we're using async SQLAlchemy, Alembic needs to run in an async context. The standard sync approach won't work with `asyncpg`.

**`0001_initial_schema.py`** creates all 5 tables in the correct dependency order:
1. `users` (no foreign keys)
2. `locations` (no foreign keys)
3. `persons` (references `locations`)
4. `events` (references `persons` and `locations`)
5. `anomaly_records` (no foreign keys, but references entities by ID as a string)

The `downgrade()` function drops everything in reverse order, and also drops the PostgreSQL `ENUM` types created for `LocationType`, `EventType`, etc.

**`alembic.ini` logging sections** — Alembic requires `[loggers]`, `[handlers]`, and `[formatters]` sections in the ini file. Without them you get `KeyError: 'formatters'`. This is a known gotcha with Alembic's logging setup.

---

## Part 7 — Authentication

Authentication in Spectra is stateless JWT-based auth. Here's the complete flow:

### Step 1: Register (`POST /api/v1/auth/register`)

1. Client sends `{"username": "demo", "password": "demo1234"}`
2. Backend checks if `username` already exists in the `users` table
3. If not, hashes the password with bcrypt and creates a `User` row
4. Generates a JWT token with the user's UUID as the `sub` claim
5. Returns `{"access_token": "eyJ...", "token_type": "bearer"}`

**Why bcrypt?** Regular hashing (MD5, SHA256) is fast — which is bad for passwords. Attackers can try billions of guesses per second. bcrypt is intentionally slow (~100ms per hash) and includes a random salt, making brute-force attacks infeasible.

### Step 2: Login (`POST /api/v1/auth/login`)

1. Client sends username + password
2. Backend looks up the user by username
3. Calls `verify_password(plain, hashed)` — bcrypt checks the hash
4. If valid, generates a new JWT
5. Returns the token

### Step 3: Authenticated request (`GET /api/v1/auth/me`)

1. Client sends `Authorization: Bearer eyJ...`
2. `get_current_user` dependency runs:
   - Extracts the token from the header
   - Calls `decode_token(token)` — verifies the JWT signature and expiry
   - Looks up the user by the `sub` (UUID) claim
   - Returns the User object
3. The route handler receives the user and can use it

**JWT anatomy:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  ← header (base64)
.eyJzdWIiOiJ1c2VyLXV1aWQiLCJleHAiOi4uLn0  ← payload (base64)
.HMAC_SHA256_signature  ← signature
```

The signature is computed using your `JWT_SECRET_KEY`. If anyone tampers with the payload (e.g., changes the `sub` to a different user's ID), the signature won't match and `decode_token` raises `JWTError`. This is why the secret key must be kept secret.

**Why embed `user.id` (UUID) not `username` in the token?**
If a user changes their username, a token containing the old username would break. A UUID never changes.

---

## Part 8 — The Ethics Guard Middleware

### File: `backend/app/middleware/ethics_guard.py`

This is Spectra's most important safety feature.

```python
_REAL_PII_PATTERNS = [
    ("real_phone_number", re.compile(r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?...")),
    ("real_ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("real_email_domain", re.compile(r"...@(?:gmail|yahoo|outlook...)...")),
    ("credit_card", re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b")),
    ("aadhaar", re.compile(r"\b[2-9]\d{3}[\s]?\d{4}[\s]?\d{4}\b")),
]
```

On every `POST`, `PUT`, or `PATCH` request:

1. Read the entire request body into memory
2. Decode it as UTF-8 text
3. Run each regex against the text
4. If any pattern matches, return `400 ETHICS_VIOLATION` immediately — the request never reaches the route handler
5. If no patterns match, re-attach the body bytes to the request and continue

**The re-attach step is critical.** HTTP request bodies can only be read once by default. After reading the bytes to check for PII, the bytes are "consumed". Without re-attaching them:
```python
async def receive():
    return {"type": "http.request", "body": body_bytes}
request._receive = receive
```
...the route handler would receive an empty body. This is an ASGI-level trick that puts the bytes back.

**Why only POST/PUT/PATCH and not GET?** GET requests don't have bodies (query strings are different). The patterns to check for are things people would send in a form or JSON body.

**Pattern choices:**
- Phone numbers: International format (`+country_code number`) is the most recognizable pattern for real phone numbers. Fake phones in Spectra use US domestic format without a `+` prefix.
- SSN: `XXX-XX-XXXX` format is unique to the US SSN. Spectra's fake SSNs use this format too — but the ethics guard catches them *before* they're stored, making the guard a deliberate design constraint that forces developers to use truly synthetic generators.
- Email: Only blocks common free provider domains. Business email addresses on fictional domains (e.g., `alice@synthetic-corp.fake`) would pass through — intentional, since the data generator creates fictional company domains.

---

## Part 9 — The FastAPI Application Shell

### File: `backend/app/main.py`

```python
app = FastAPI(title="Spectra API", ...)

app.add_middleware(EthicsGuardMiddleware)  ← outermost
app.add_middleware(CORSMiddleware, ...)    ← inner

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "project": "Spectra"}
```

**Middleware order matters.** FastAPI processes middleware like an onion — the first `add_middleware` call is the outermost layer. Requests pass through it first (inbound) and responses pass back through it last (outbound). By putting `EthicsGuardMiddleware` first, it wraps everything — PII is blocked before CORS headers are even evaluated.

**Why `CORSMiddleware` inline rather than in `cors.py`?** The original plan was a separate file, but during implementation the AI placed it directly in `main.py` — which is functionally identical. The `FOLDER_STRUCTURE.md` listed a separate file as a suggestion, not a hard requirement.

**The `/health` endpoint** is used by Docker's healthcheck and by deployment platforms (Railway, etc.) to verify the service is alive. It intentionally does no database query — it should return `200 OK` even if the DB is down.

---

## Part 10 — The Frontend

### File: `frontend/vite.config.ts`

```javascript
proxy: {
  '/api': { target: 'http://localhost:8000', changeOrigin: true },
  '/health': { target: 'http://localhost:8000', changeOrigin: true },
}
```

In development, the frontend runs on port 5173. The backend is on 8000. Browsers block cross-origin requests unless CORS headers are set. Rather than dealing with CORS in development, Vite's dev server proxies `/api/*` requests to the backend transparently. From the browser's perspective, everything is on `localhost:5173` — no cross-origin issue.

**`changeOrigin: true`** makes the proxy rewrite the `Host` header to match the target, preventing the backend from seeing `localhost:5173` as the origin.

### File: `frontend/src/components/layout/EthicsBanner.tsx`

This component is mounted in `DashboardPage.tsx` and will be mounted in every page created in Phase 4. Key design decisions:

- `fixed top-0 left-0 right-0 z-50` — anchored to the top of the viewport, always visible regardless of scroll
- `role="banner"` — semantic HTML for accessibility; screen readers announce this as a landmark
- Not dismissible — no X button, no close logic. This is intentional and must never change.
- The CSS variable `--ethics-banner-height: 52px` is set in `index.css` and used as `padding-top` on `.page-content`. This prevents page content from hiding behind the fixed banner.

### File: `frontend/src/App.tsx`

Currently just one route: `/` → `DashboardPage`. Phase 4 will add `/map`, `/graph`, `/anomalies`, `/search`, `/about`. The route structure is already stubbed in comments.

---

## Part 11 — Tests

### `test_ethics_guard.py`

Five tests that verify:
1. A real phone number (`+91 98765 43210`) is blocked
2. A US SSN (`523-45-6789`) is blocked
3. A Gmail address (`john.doe@gmail.com`) is blocked
4. Synthetic data with no real PII passes through
5. An empty body passes through

Each test creates a minimal FastAPI app with only the ethics guard middleware and one test endpoint, wrapped in a `TestClient`. This tests the middleware in isolation from the rest of the app.

### `test_auth_service.py`

Five tests that verify the pure functions in `auth_service.py`:
1. `hash_password` returns a bcrypt-formatted string (`$2b$...`)
2. `verify_password` returns `True` for the correct password
3. `verify_password` returns `False` for the wrong password
4. A freshly created JWT can be decoded back to the same `sub`
5. An expired JWT raises `JWTError`

These tests have zero external dependencies — no database, no network, no Docker. They test only the cryptographic logic.

### `conftest.py`

Two fixtures:
- `test_client` — a synchronous FastAPI `TestClient` wrapping the full app. `raise_server_exceptions=False` means HTTP 4xx/5xx responses are returned to your test instead of raising Python exceptions.
- `test_db` — an in-memory SQLite session. Creates all tables before each test, drops them after. The `PRAGMA foreign_keys=ON` line enables FK enforcement in SQLite (off by default), so your tests catch FK violations.

---

## Interview Questions You Should Be Able to Answer

After reading this document, you should be able to answer all of these:

**On Docker:**
- Why are healthchecks important in docker-compose?
- What does `depends_on: condition: service_healthy` do?
- Why is mounting `./backend:/app` as a volume useful in development?

**On the database:**
- What is async SQLAlchemy and why do we use it with FastAPI?
- What is connection pooling? What do `pool_size` and `max_overflow` control?
- What is `pool_pre_ping` and why is it useful?
- What is Alembic? Why not just use `create_all()`?
- Why use UUID primary keys instead of auto-increment integers?

**On authentication:**
- Explain the full JWT auth flow from register to authenticated request
- Why is bcrypt better than SHA256 for passwords?
- What's in a JWT? What does the signature prove?
- Why embed the user's UUID (not username) in the JWT `sub` claim?

**On middleware:**
- What is ASGI middleware? How does it differ from a route handler?
- Why does the Ethics Guard re-attach the body bytes after reading them?
- Why is `EthicsGuardMiddleware` registered before `CORSMiddleware`?

**On architecture:**
- Why is the ethics guard middleware instead of a function called from each route?
- What is the purpose of the `_synthetic: true` metadata field?
- What is the difference between `deps.py` (dependencies) and `services/` (business logic)?

---

## What Phase 2 Will Build

Phase 2 takes this skeleton and gives it data to work with:

- `PersonGenerator` — creates fake people using the `Faker` library
- `LocationGenerator` — creates fake lat/lon coordinates and building types
- `EventGenerator` — creates fake calls, messages, meetings, and money transfers between people
- `GET /persons`, `GET /locations`, `GET /events` REST endpoints
- The CLI command: `python -m app.data_gen.run --persons 500 --events 2000`

After Phase 2, you'll be able to hit the API and get back thousands of rows of realistic-looking synthetic data.

---

*Document version: 1.0 — Generated for Spectra Phase 1 completion*
*Next document: PHASE-2-EXPLANATION.md (generated after Phase 2)*
