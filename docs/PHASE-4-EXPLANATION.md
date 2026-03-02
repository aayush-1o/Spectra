"""
Phase 4 — Frontend + Backend Integration: Full Explanation

## 1. Architecture Overview

```
React SPA (Vite + TailwindCSS v4)
├── Auth Context (localStorage JWT, cross-tab sync)
├── Protected Routes (React Router v7)
├── Axios Client (Bearer injection + 401 redirect)
└── 8 Pages wired to live FastAPI backend
```

## 2. New Files Created

| File | Purpose |
|------|---------|
| `src/types/index.ts` | All TypeScript interfaces (mirror Pydantic schemas) |
| `src/api/client.ts` | Axios singleton + JWT interceptor + 401→login redirect |
| `src/api/*.ts` | One file per resource: auth, persons, events, locations, graph, anomalies |
| `src/store/auth.tsx` | React Context: token, isAuthenticated, login(), logout() |
| `src/hooks/useAuth.ts` | `useContext(AuthContext)` convenience hook |
| `src/hooks/useApi.ts` | Generic `{ data, loading, error, refetch }` fetching hook |
| `src/components/layout/EthicsBanner.tsx` | Fixed top banner on every page |
| `src/components/layout/Sidebar.tsx` | NavLink sidebar with active styling |
| `src/components/layout/Layout.tsx` | Root shell: banner + sidebar + content |
| `src/components/ui/KpiCard.tsx` | Stat card with loading skeleton |
| `src/components/ui/LoadingSpinner.tsx` | SVG spinner |
| `src/components/ui/ErrorMessage.tsx` | Rose error box |
| `src/components/ui/Badge.tsx` | Color badge/pill |
| `src/components/ui/Pagination.tsx` | Prev/Next with disabled states |
| `src/components/graph/CytoscapeGraph.tsx` | Cytoscape.js wrapper (cose layout, Person/Location styles) |
| `src/pages/LoginPage.tsx` | Form → API login → store token → `/` |
| `src/pages/RegisterPage.tsx` | Form → register → auto-login → `/` |
| `src/pages/DashboardPage.tsx` | KPI cards (persons, events, anomalies) + events feed |
| `src/pages/MapPage.tsx` | React-Leaflet map with location markers + event popups |
| `src/pages/GraphPage.tsx` | Person search → Cytoscape neighbourhood (hop slider) |
| `src/pages/AnomaliesPage.tsx` | Sortable table + run-detection button + pagination |
| `src/pages/SearchPage.tsx` | Debounced person search grid → navigate to graph |
| `src/pages/AboutPage.tsx` | Ethics notice, principles, tech stack |
| `src/App.tsx` | All 8 routes + ProtectedRoute + PublicRoute guards |
| `src/main.tsx` | Entry: AuthProvider wraps App |
| `src/tests/setup.ts` | Vitest setup: imports jest-dom matchers |
| `src/tests/api.client.test.ts` | 5 unit tests: token injection + debounce |
| `src/tests/useAuth.test.tsx` | 3 unit tests: login/logout state transitions |

## 3. How to Run

### Development
```bash
# Ensure backend + Neo4j running:
docker compose up -d

# Start frontend dev server:
cd frontend
npm run dev
# → http://localhost:5173
```

### Production Build
```bash
cd frontend && npm run build
```

### Tests
```bash
cd frontend && npm run test
```

## 4. Common Bugs

### "Cannot GET /api/..." (404 during dev)
**Cause**: Backend not running. Vite proxy needs the FastAPI server at :8000.
**Fix**: `docker compose up -d` first, then `npm run dev`.

### Map page shows tiles but no markers
**Cause**: No location data seeded yet.
**Fix**: `docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800`

### Leaflet icon broken (gray box instead of pin)
**Cause**: Vite's bundler breaks Leaflet's default icon path resolution.
**Fix** (already applied): Delete `_getIconUrl` prototype and use `mergeOptions` with unpkg CDN URLs.

### Graph page: "No path found" error
**Cause**: The two persons have no connection in Neo4j.
**Fix**: Run `graph_builder` first: `docker exec spectra-backend python -m app.data_gen.graph_builder`

### Anomaly table empty
**Cause**: Detection hasn't run yet.
**Fix**: Click "Run Detection" on the Anomalies page (or `POST /api/v1/anomalies/run-detection`).

### "act(...)" warning in Vitest
**Cause**: useAuth.test.tsx triggers async state updates without `act()` wrapping inside jsdom.
**Impact**: Zero — tests pass. It's a React 19 + jsdom diagnostic warning.

## 5. Manual Debugging Checklist

```bash
# 1. Check all containers healthy
docker ps

# 2. Verify backend responds
curl http://localhost:8000/health

# 3. Check frontend dev server running
curl http://localhost:5173

# 4. Test auth endpoint directly
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo2","password":"demo1234"}'

# 5. Refresh localStorage in browser devtools
# Application → Local Storage → localhost:5173 → spectra_token

# 6. Trigger Neo4j error (no connection)
# → Check NEO4J_URI env var in docker-compose.yml

# 7. Test Vitest in watch mode for TDD
cd frontend && npm run test:watch
```

## 6. Known Edge Cases

| Case | Behaviour |
|------|-----------|
| Expired JWT | 401 interceptor clears token + redirects to /login |
| Same username register | Backend returns 400; error shown on form |
| Graph with 0 results | Empty state illustration shown |
| Anomaly detection running | Button shows spinner, disabled |
| Large anomaly list | Pagination with prev/next (20 per page) |
| Tab LocalStorage clear | cross-tab sync via `storage` event listener |
"""
