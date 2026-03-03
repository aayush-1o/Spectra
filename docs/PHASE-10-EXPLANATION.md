# Spectra — Phase 10 Explanation
# CesiumJS 3D Globe Intelligence Platform

## What Was Built

Phase 10 replaces the flat Deck.gl + MapLibre map on `/live-map` with a **full 3D globe** powered by **CesiumJS + Resium**.  
The result is a Palantir WorldView-inspired tactical HUD with real-time asset tracking on a rotating Earth.

All data remains **100% synthetic** — no real ADS-B, GPS, or sensor feeds.

---

## What Changed vs Phase 9

| Area | Phase 9 | Phase 10 |
|------|---------|----------|
| Globe | Flat 2D map (Deck.gl + MapLibre) | 3D rotating Earth (CesiumJS) |
| Basemap | `openfreemap.org` vector tiles | Cesium Ion World Imagery (satellite) |
| Asset icons | Deck.gl `IconLayer` SVGs | Resium `BillboardCollection` — same SVGs, altitude-aware |
| Trails | Deck.gl `PathLayer` | Cesium `PolylineCollection` with glow material |
| Visual modes | None | Normal / Night Vision / Thermal / Tactical (CSS filters) |
| HUD | Light-theme white cards | Dark tactical HUD — classification banner, UTC clock, cursor coords |
| Classification | None | `TS // SI-TK // NOFORN — SYNTHETIC DATA ONLY` red banner |
| Typography | Mixed fonts | JetBrains Mono throughout for all telemetry data |
| Theme | Palantir light theme | Deep navy `#050810` dark tactical theme |

---

## Architecture

```
Browser (React)                          Backend (FastAPI)
────────────────────────────────         ──────────────────────────────
AssetTrackingPage.tsx                    /api/v1/stream/assets (WebSocket)
  ├─ useAssetStream hook (UNCHANGED)     Same as Phase 9
  ├─ Cesium.Ion.defaultAccessToken ←── VITE_CESIUM_TOKEN env var
  │
  ├─ <Viewer>  (Resium, full-screen)
  │   ├─ <BillboardCollection>  ← assets at 3D altitude
  │   └─ <PolylineCollection>   ← ghost trails
  │
  └─ HUD (HTML divs over canvas, z-index > Cesium)
      ├─ Classification banner (top)
      ├─ SPECTRA logo + connection status (top-left)
      ├─ UTC clock + cursor coordinates (top-right)
      ├─ Mode toggles Normal/NV/Thermal/Tactical (top-right)
      ├─ Asset list panel (left)
      ├─ Selected asset detail (right, click-to-open)
      └─ <TimeScrubber> (bottom, UNCHANGED)
```

---

## Visual Mode Implementation

Each mode is a CSS `filter` applied to the Cesium `<div>` wrapper:

| Mode | CSS Filter |
|------|-----------|
| **Normal** | `none` |
| **Night Vision** | `brightness(0.65) hue-rotate(88deg) saturate(4) sepia(0.55)` — green tint |
| **Thermal** | `brightness(0.8) sepia(1) saturate(6) hue-rotate(-28deg)` — orange/red |
| **Tactical** | `brightness(0.45) saturate(0.15) contrast(1.5)` + SVG grid overlay |

Night Vision also adds a scanline overlay (repeating CSS gradient).  
Tactical adds a green `60px` CSS grid overlay (pointer-events: none).

---

## Cesium Ion Token

The globe uses **Cesium Ion World Imagery** (satellite tiles), which requires a free Ion token:

1. Sign up at [ion.cesium.com](https://ion.cesium.com) (free)
2. Copy your Default Token
3. Add to `frontend/.env`:
   ```
   VITE_CESIUM_TOKEN=<your_token>
   ```

Without a token, Cesium renders a solid-colour globe (still 3D). The app does **not** crash — it gracefully degrades.

---

## Altitude Rendering

Assets are placed at Cesium 3D positions using `Cartesian3.fromDegrees(lon, lat, altitude)`:

| Type | Minimum Altitude |
|------|-----------------|
| `flight` | `max(data.altitude_m, 3000)` — always visibly above globe |
| `drone` | `max(data.altitude_m, 50)` — low-altitude but above surface |
| `vehicle` | `CLAMP_TO_GROUND` — HeightReference snaps to terrain |

---

## Vite Configuration

Cesium requires its web workers and static assets to be served at a known path.  
`vite-plugin-static-copy` copies `cesium/Build/Cesium/{Workers,ThirdParty,Assets,Widgets}` → `public/cesium/`.  
`define: { CESIUM_BASE_URL: '"/cesium"' }` tells Cesium where to look at runtime.

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/pages/AssetTrackingPage.tsx` | Full replacement — CesiumJS globe + HUD |
| `frontend/vite.config.ts` | Added `vite-plugin-static-copy` + `CESIUM_BASE_URL` define |
| `frontend/index.html` | Added JetBrains Mono + Cesium widgets CSS |
| `frontend/.env` | Added `VITE_CESIUM_TOKEN` |
| `package.json` | Added `resium`, `cesium`, `vite-plugin-static-copy` |

**Unchanged:** `useAssetStream.ts`, `TimeScrubber.tsx`, `telemetry.ts`, all backend files.

---

## How To Run

```bash
# Install new frontend dependencies (already done if you ran npm install)
cd frontend && npm install

# Start dev server
npm run dev

# Visit
open http://localhost:5173/live-map
```

---

## Debugging Guide

### Globe is black / solid colour
**Cause:** Missing or invalid `VITE_CESIUM_TOKEN`.  
**Fix:** Add `VITE_CESIUM_TOKEN=<your_token>` to `frontend/.env`, restart dev server.

### Cesium workers 404
**Symptom:** Console errors like `Failed to fetch /cesium/Workers/xx.js`.  
**Cause:** `vite-plugin-static-copy` didn't run, or `CESIUM_BASE_URL` mismatch.  
**Fix:**
```bash
# Confirm 383 items collected:
npm run dev | grep "Collected"
# Should output: [vite-plugin-static-copy] Collected 383 items.
```

### Assets not visible on globe
**Cause A:** WebSocket not connected — `assetList` is empty.  
**Cause B:** `VITE_API_BASE_URL` pointing to wrong backend.  
**Fix:** Check Network tab for WS frames; try `curl http://localhost:8000/api/v1/stream/assets/snapshot`.

### Mode toggle doesn't change appearance
CSS filters are applied to the globe wrapper `div`. If Tailwind CSS purges a class, the filter may not apply.  
All mode filters are inline styles (not Tailwind classes) — this cannot happen.

### TimeScrubber shows 0 frames
Wait 5–10 seconds after opening the page. History fills at 1 frame/second.
