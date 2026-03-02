# Phase 2 — Synthetic Data Engine: Full Explanation

> **Project**: Spectra (SimSight)
> **Phase**: 2 — Synthetic Data Engine
> ⚠️ ALL DATA IS FAKE. No real people. No real surveillance. Educational only.

---

## 1. What Each Generator Class Does

### `PersonGenerator` (`app/data_gen/person_generator.py`)

Produces unsaved SQLAlchemy `Person` ORM objects. It does **not** write to the database — the caller is responsible for `session.add_all()`.

| Field | How it's generated |
|-------|--------------------|
| `fake_name` | `Faker().name()` — realistic full name string |
| `date_of_birth` | `date.today() - timedelta(days=random.randint(20*365, 70*365))` |
| `occupation` | `random.choice(constants.OCCUPATIONS)` — 20 fictional job titles |
| `metadata_` | Always `{"_synthetic": True}` |

**Design decision**: Age is bounded to 20–70 years because extremes (under 18 or 80+) are not relevant to the surveillance sim scenario and would require special handling.

---

### `LocationGenerator` (`app/data_gen/location_generator.py`)

Uses **numpy** to generate a cluster of coordinates around fictional "New Meridian City".

| Field | How it's generated |
|-------|--------------------|
| `lat` / `lng` | `np.random.normal(city_centre, bbox/3, n)` clipped to bounding box |
| `fake_address` | `"{num} {Prefix} {Suffix}, New Meridian City"` |
| `location_type` | `random.choice(list(LocationType))` |
| `metadata_` | Always `{"_synthetic": True}` |

**Design decision**: Gaussian distribution (not uniform) makes the data cluster realistically — most activity near the city centre with fewer outliers. The standard deviation is `BBOX_DELTA / 3` so ~99.7% of points fall within the bounding box.

---

### `EventGenerator` (`app/data_gen/event_generator.py`)

Pairs persons into synthetic interactions.

| Field | How it's generated |
|-------|--------------------|
| `actor_id`, `target_id` | `random.sample(persons, 2)` — guaranteed distinct |
| `event_type` | `random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)` — weighted |
| `occurred_at` | Random day offset + business-hours-weighted hour |
| `location_id` | `random.choice(locations).id` |
| `metadata_` | `{"_synthetic": True}` + type-specific fields |

**Event type metadata extras**:
- `call` → `duration_seconds` (60–3600)
- `transfer` → `amount_usd` (10.00–50,000.00)

**Design decision**: `random.sample(persons, 2)` guarantees actor ≠ target in a single call, avoiding a retry loop.

---

## 2. How Faker Is Used

Faker is imported once at module level as a singleton `_faker = Faker()` to avoid the overhead of instantiation per record.

| Faker method | Field produced | Example output |
|---|---|---|
| `_faker.name()` | `Person.fake_name` | `"Dr. Maria Nguyen"` |

Only `.name()` is used in Phase 2. Faker's locale defaults to `en_US`. No seed is set (data is non-deterministic by design).

---

## 3. How NumPy Is Used

### Coordinate generation (`location_generator.py`)
```python
lats = np.clip(
    np.random.normal(CITY_CENTRE_LAT, BBOX_DELTA / 3, n),
    CITY_CENTRE_LAT - BBOX_DELTA,
    CITY_CENTRE_LAT + BBOX_DELTA,
)
```
All `n` lat/lon values are generated **vectorised** in a single NumPy call — much faster than a Python loop for large `n`.

### Business-hours time distribution (`event_generator.py`)
```python
_HOUR_WEIGHTS = [3.0 if 9 <= h <= 17 else 1.0 for h in range(24)]
hour = int(np.random.choice(_HOURS, p=_HOUR_WEIGHTS_NORM))
```
Hours 9am–5pm are 3× more likely than off-hours, creating a realistic activity pattern.

---

## 4. How `run.py` Orchestrates the Pipeline

```
argparse (--persons, --events)
        ↓
PersonGenerator.generate(n_persons)   → list of unsaved Person objects
LocationGenerator.generate(n_locations) → list of unsaved Location objects
        ↓
async DB session opened (get_async_session)
        ↓
session.add_all(persons) → session.flush()  ← assigns PKs
session.add_all(locations) → session.flush() ← assigns PKs
        ↓
EventGenerator.generate(persons, locations, n_events)
        ↓
session.add_all(events) → session.commit()
        ↓
Print timing summary + counts
```

**Critical**: `flush()` is called before generating events so the ORM objects have their `.id` values set (UUIDs are assigned at Python construction by `UUIDMixin`, but `flush()` confirms them in the DB transaction before events reference them as FKs).

`n_locations = max(n_persons // 4, 10)` — quarter of persons, minimum 10.

---

## 5. How Pagination Is Implemented

All three GET endpoints use SQLAlchemy async select with `.offset().limit()`:

```python
stmt = select(Person)
if search:
    stmt = stmt.where(Person.fake_name.ilike(f"%{search}%"))
stmt = stmt.offset(offset).limit(limit).order_by(Person.created_at.desc())
result = await db.execute(stmt)
return result.scalars().all()
```

**Limit enforcement**: `if limit > 100: raise HTTPException(422)`. FastAPI's built-in `ge=1` on the Query ensures minimum of 1.

The events endpoint additionally supports filtering by `event_type`, `from_date`, and `to_date` via `.where()` clauses chained onto the statement.

---

## 6. How To Run Data Generation (Step by Step)

```bash
# Step 1: Ensure Docker is running
docker compose up --build

# Step 2: Apply migrations
docker exec spectra-backend alembic upgrade head

# Step 3: Generate data
docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800

# Expected output:
# [Spectra] Generating 200 persons, 50 locations, 800 events …
# [Spectra] ✅ Done in 0.43s — 200 persons | 50 locations | 800 events inserted.

# Step 4: Verify in psql
docker exec -it spectra-db psql -U simsight -d simsight -c "SELECT COUNT(*) FROM persons;"
docker exec -it spectra-db psql -U simsight -d simsight -c "SELECT COUNT(*) FROM events;"
```

---

## 7. Common Bugs and Fixes

### `ModuleNotFoundError: No module named 'app'`
**Cause**: Running `python run.py` directly instead of `python -m app.data_gen.run`.
**Fix**: Always use `python -m app.data_gen.run` from the `/app` working directory inside Docker.

### Generator produces 0 events
**Cause**: Fewer than 2 persons in the list.
**Fix**: EventGenerator raises `ValueError("Need at least 2 persons...")` before 0 events are returned. Ensure persons list has ≥ 2 items.

### API returns 401 Unauthorized
**Cause**: No `Authorization: Bearer <token>` header, or token expired (default 60 min).
**Fix**: Register → login → copy `access_token` → pass as `Authorization: Bearer <token>`.

### `metadata_` vs `metadata` confusion
**Cause**: The Python attribute is `metadata_` but the DB column is `"metadata"`. SQLAlchemy maps them via `mapped_column("metadata", ...)`.
**Fix**: Always use `.metadata_` in Python code. Never rename this attribute.

### `asyncpg.exceptions.ConnectionRefusedError`
**Cause**: PostgreSQL container not yet ready when backend starts.
**Fix**: `docker-compose.yml` has a `healthcheck` + `depends_on: condition: service_healthy`. If it still fails, wait 5 seconds and retry.

---

## 8. Manual Debugging Guide — Inspecting Data in psql

```bash
# Connect to postgres
docker exec -it spectra-db psql -U simsight -d simsight

# Count all tables
SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;

# Sample 5 persons
SELECT id, fake_name, occupation, date_of_birth FROM persons LIMIT 5;

# Sample 5 events with types
SELECT event_type, actor_id, target_id, occurred_at FROM events LIMIT 5;

# Count by event type
SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY count DESC;

# Check metadata contains _synthetic
SELECT COUNT(*) FROM events WHERE metadata->>'_synthetic' = 'true';

# Verify no self-events
SELECT COUNT(*) FROM events WHERE actor_id = target_id;  -- should be 0
```

---

## 9. Interview Questions You Should Be Able to Answer

**Q: Why do all records have `_synthetic: True` in metadata?**
A: It's a non-negotiable safety invariant. Any downstream system (reporting, export) can filter out synthetic data by checking this flag. It also makes it obvious in psql that no real data was accidentally inserted.

**Q: Why use `flush()` before generating events?**
A: `flush()` sends the INSERT to the DB within the transaction without committing. This confirms PKs are assigned (even though UUIDs are set by Python defaults at object creation). It ensures FK constraints on `actor_id`/`target_id` will be satisfied when events are added in the same transaction.

**Q: Why is business-hours weighting implemented with numpy `np.random.choice(p=...)` instead of `random.choices(...)`?**
A: `np.random.choice` with `p` parameter accepts a probability array natively. It's equivalent to `random.choices` with weights but integrates cleanly into numpy-heavy code. Either would work; numpy was already imported for coordinates.

**Q: What would happen if you called `generate()` generators without `session.add_all()`?**
A: The objects would exist in Python memory but never reach the database. No error would be raised. The next `session.commit()` on those objects wouldn't persist them since they were never added to the session.

**Q: How does the ILIKE search work in async SQLAlchemy?**
A: `Person.fake_name.ilike(f"%{search}%")` generates `WHERE fake_name ILIKE '%term%'`. ILIKE is PostgreSQL's case-insensitive LIKE. The `%` wildcards match any characters before/after the search term. This is translated to a parameterized query — no SQL injection risk.

**Q: Why is the events `type` query param named `type` and not `event_type`?**
A: API query parameters are named for the API consumer's convenience — `?type=call` is cleaner. Inside the handler, it's mapped to the `EventType` enum. Using `type` is a common REST convention for filtering by resource type.
