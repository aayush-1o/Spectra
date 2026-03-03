# Phase 9 — 3D Geospatial & Real-Time Asset Tracking

## What Was Built

Phase 9 adds a live 3D geospatial dashboard to Spectra, styled after Palantir Gotham's mission-tracking view.
All data is **100% synthetic** — no real ADS-B, GPS, or OpenSky feeds are used anywhere.

---

## Architecture

```
Browser (React)                     Backend (FastAPI)
──────────────────                  ─────────────────────────────────────────
AssetTrackingPage                   /api/v1/stream/assets   (WebSocket)
  └─ useAssetStream hook            /api/v1/stream/assets/snapshot (REST)
       └─ WebSocket client   ←────  stream.py router
            1 Hz frames             └─ synthetic_telemetry.py
                                         TelemetryGenerator
                                         Fleet of 20 fake assets
                                         Waypoint interpolation (math only)
```

### Telemetry Generator (`synthetic_telemetry.py`)

| Asset Type | Count | Altitude | Speed | Icon |
|------------|-------|----------|-------|------|
| Drone      | 8     | 50–300 m | 30–80 km/h | 🚁 |
| Flight     | 4     | 5 000–12 000 m | 600–900 km/h | ✈ |
| Vehicle    | 8     | 0 m | 20–80 km/h | 🚗 |

- Uses **haversine distance** + **linear waypoint interpolation** — pure math, no external data
- Each asset gets a random callsign (`UAV-GHO001`, `FLT-RAV002`, etc.) based on the existing `FAKE_ALIASES` constant
- Assets loop indefinitely on their waypoint circuits
- Module-level `get_fleet()` singleton ensures all WebSocket connections share the same moving fleet

### WebSocket Endpoint (`stream.py`)

Protocol (two message types):
1. **On connect** → `{"type": "manifest", "synthetic": true, "assets": [{id, label, asset_type}, ...]}`
2. **Every 1 second** → `{"type": "positions", "data": [AssetPosition, ...]}`

A `ConnectionManager` tracks all active WebSocket clients.
The REST snapshot endpoint (`GET /api/v1/stream/assets/snapshot`) returns the same positions without needing a WebSocket handshake — used for the initial render.

### Frontend

| File | Purpose |
|------|---------|
| `types/telemetry.ts` | TypeScript types for all stream messages |
| `hooks/useAssetStream.ts` | WebSocket lifecycle, exponential back-off, history buffer |
| `components/map/TimeScrubber.tsx` | Play/Pause/Speed/Live controls |
| `pages/AssetTrackingPage.tsx` | Full-screen Deck.gl + MapLibre map page |

**Map stack:**
- **Deck.gl** — `IconLayer` (asset icons), `PathLayer` (ghost trails), `TextLayer` (callsign labels)
- **MapLibre GL** — base map tiles via `https://demotiles.maplibre.org/style.json` (**zero API key required**)
- **react-map-gl** — React bindings for MapLibre

---

## Design Decisions

### Why Deck.gl instead of extending Leaflet?

Leaflet is a 2D canvas/SVG library. Deck.gl uses **WebGL 2** which enables:
- Real 3D pitch/tilt view (the `pitch: 45` default)
- Rendering 1 000+ icons at 60 fps with `IconLayer`
- Ghost trail `PathLayer` rendered on the GPU
- No DOM overhead for markers (1 `<canvas>` element for the whole map)

The existing Leaflet page (`/map`) is preserved 100% untouched at its own route.

### Why MapLibre instead of Mapbox?

Mapbox GL JS v2+ requires a paid API key even for free-tier usage. MapLibre is the open-source fork (MIT licence) with identical APIs. The `demotiles.maplibre.org` tile server is free, no key required.

### Why a module-level fleet singleton?

If each WebSocket connection created its own fleet, different browser tabs would see different asset positions. The singleton means all clients observe the same 20 assets moving coherently.

### Why exponential back-off in `useAssetStream`?

WebSocket connections drop silently in serverless/container environments (idle timeouts, deploy restarts). Back-off (1 s → 2 s → 4 s → … → 30 s) prevents hammering the server while staying responsive.

### Why a rolling 2-minute history buffer?

120 seconds at 1 Hz = 120 frames. At 20 assets × ~200 bytes each = ~4.8 MB max — well within browser memory. The time scrubber needs this buffer for replay; older frames are pruned automatically.

---

## How To Run

### Local Docker (recommended)

```bash
# 1. Rebuild containers with Phase 9 code
docker compose up --build -d

# 2. Run all migrations (no new schema changes in Phase 9)
docker exec spectra-backend alembic upgrade head

# 3. Open the frontend
open http://localhost:5173/live-map
```

### Verify the WebSocket feed directly

```bash
# Using websocat (brew install websocat)
websocat ws://localhost:8000/api/v1/stream/assets

# Or using the REST snapshot
curl http://localhost:8000/api/v1/stream/assets/snapshot | python3 -m json.tool
```

### Run Phase 9 tests

```bash
# Inside container
docker exec spectra-backend pytest tests/test_phase9.py -v

# Or locally (if venv is active)
cd backend && pytest tests/test_phase9.py -v
```

Expected output: **18 passed** across:
- `TestTelemetryGenerator` — 12 tests
- `TestHelpers` — 4 tests
- `TestStreamSnapshotEndpoint` — 6 tests
- `TestAssetStreamWebSocket` — 3 tests

---

## Feature walkthrough

| Feature | How to test |
|---------|------------|
| Live tracking | Open `/live-map` — status bar shows 🟢 LIVE |
| Moving icons | Watch ✈ 🚁 🚗 icons drift across the map |
| Ghost trails | Coloured path segments trail each asset |
| Click an asset | Click any icon → detail popup (lat/lon/altitude/speed/heading) |
| Asset list | Left panel lists all assets; click to select |
| 2D / 3D toggle | Top-right buttons toggle pitch 0° / 45° |
| Replay | Press ▶ on time scrubber → assets replay from history |
| Speed | Click 1× / 2× / 5× to change playback speed |
| Live lock | Click LIVE button → snaps back to real-time feed |
| Disconnect | Stop backend → badge turns 🔴 DISCONNECTED, reconnects automatically |

---

## Common Bugs & Manual Debugging Guide

### 1. WebGL Context Loss

**Symptom:** Map goes black; console shows `WebGL context lost`.

**Cause:** GPU memory pressure (too many WebGL contexts, heavy other tabs) or driver crash.

**Fix:**
```
1. Refresh the page (context is automatically restored on reconnect).
2. Close other tabs using WebGL (Three.js, other maps).
3. If persistent: Chrome → chrome://gpu → check "Software rendering" — update GPU driver.
4. As a workaround, add `preserveDrawingBuffer: true` to DeckGL props.
```

### 2. WebSocket Disconnects / "DISCONNECTED" badge

**Symptom:** Badge turns red, no positions update.

**Cause A:** Backend crashed or restarted (check `docker logs spectra-backend`).
**Cause B:** Browser went idle / laptop slept — OS closes idle TCP connections.
**Cause C:** CORS issue on WebSocket handshake.

**Fix:**
```bash
# Check backend
docker logs spectra-backend --tail=50

# Restart
docker compose restart spectra-backend

# WebSocket CORS: ensure settings.cors_origins includes 'http://localhost:5173'
```
The `useAssetStream` hook auto-reconnects with exponential back-off (1 s → 30 s).

### 3. Map tiles don't load (grey map)

**Symptom:** Deck.gl canvas renders, but no map tiles appear.

**Cause:** `demotiles.maplibre.org` is a public demo server — it can be rate-limited or temporarily down.

**Fix:**
```
1. Check https://demotiles.maplibre.org/style.json in the browser.
2. Alternative free tile: change mapStyle in AssetTrackingPage.tsx to:
   "https://tiles.openfreemap.org/styles/liberty"
3. Or use a local tile server with Docker:
   docker run -p 8080:80 maptiler/tileserver-gl
   then set style to "http://localhost:8080/styles/basic-preview/style.json"
```

### 4. Icons not visible (blank canvas)

**Symptom:** Map loads, no icons appear.

**Cause A:** WebSocket not connected → `assetList` is empty. Check Network tab for WS frames.
**Cause B:** SVG icon atlas failed to encode. Check console for `btoa` errors.
**Cause C:** `VITE_API_BASE_URL` env var points to wrong host.

**Fix:**
```bash
# Check env
echo $VITE_API_BASE_URL   # should be http://localhost:8000

# Test snapshot
curl http://localhost:8000/api/v1/stream/assets/snapshot

# Check browser console for Deck.gl icon mapping errors
```

### 5. Time scrubber shows "0 frames"

**Symptom:** Scrubber slider is disabled, no history.

**Cause:** WebSocket not yet connected, or browser just opened (history buffer starts empty).

**Fix:** Wait ~5 seconds for frames to accumulate. The buffer grows at 1 frame/second.

### 6. `Cannot find module 'maplibre-gl'` build error

**Cause:** npm packages not installed.

**Fix:**
```bash
cd frontend && npm install
```

---

## New Files Summary

| File | Type | Description |
|------|------|-------------|
| `backend/app/data_gen/synthetic_telemetry.py` | New | Fleet generator + tick engine |
| `backend/app/api/v1/stream.py` | New | WebSocket + REST snapshot router |
| `backend/tests/test_phase9.py` | New | 18 unit tests |
| `frontend/src/types/telemetry.ts` | New | TypeScript types |
| `frontend/src/hooks/useAssetStream.ts` | New | WS lifecycle hook |
| `frontend/src/components/map/TimeScrubber.tsx` | New | Timeline control |
| `frontend/src/pages/AssetTrackingPage.tsx` | New | 3D map page |
| `frontend/src/App.tsx` | Modified | Added `/live-map` route |
| `frontend/src/components/layout/Sidebar.tsx` | Modified | Added 🛰 Live Tracking nav link |
| `backend/app/main.py` | Modified | Registered stream router, v0.9.0 |
| `docs/HANDOFF.md` | Modified | Phase 9 status |
