/**
 * Spectra — Map Page (Phase 8)
 * Renders synthetic locations as pins OR heatmap using leaflet.heat.
 */
import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'
import { useApi } from '../hooks/useApi'
import { listLocations } from '../api/locations'
import { listEvents } from '../api/events'
import type { Location } from '../types'

// Fix Leaflet default icon paths broken by Vite bundling
// @ts-expect-error private property
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// ── Heatmap layer component ────────────────────────────────────────────────────
interface HeatmapLayerProps {
    points: [number, number, number][]  // [lat, lng, intensity]
}

function HeatmapLayer({ points }: HeatmapLayerProps) {
    const map = useMap()
    const layerRef = useRef<unknown>(null)

    useEffect(() => {
        if (!points.length) return

        // Dynamically import leaflet.heat
        import('leaflet.heat').then(() => {
            const heat = L.heatLayer(points, {
                radius: 35,
                blur: 25,
                maxZoom: 15,
                gradient: { 0.2: '#2563eb', 0.5: '#f59e0b', 0.8: '#ef4444' },
            })
            heat.addTo(map)
            layerRef.current = heat

            return () => {
                map.removeLayer(heat)
            }
        }).catch(console.error)

        return () => {
            if (layerRef.current) {
                // @ts-expect-error
                map.removeLayer(layerRef.current)
            }
        }
    }, [map, points])

    return null
}

export default function MapPage() {
    const locations = useApi(() => listLocations({ limit: 100 }))
    const events = useApi(() => listEvents({ limit: 200 }))
    const [viewMode, setViewMode] = useState<'pins' | 'heatmap'>('pins')

    // Inject Leaflet dark tile — no extra CSS needed
    useEffect(() => {
        const style = document.createElement('style')
        style.textContent = `.leaflet-container { background: #0d1117 !important; }`
        document.head.appendChild(style)
        return () => { document.head.removeChild(style) }
    }, [])

    const center: [number, number] = locations.data?.[0]
        ? [locations.data[0].lat, locations.data[0].lng]
        : [51.5074, -0.1278]

    // Build heatmap points: [lat, lng, intensity] where intensity = event count
    const heatmapPoints: [number, number, number][] = []
    if (locations.data && events.data) {
        const eventsByLocation: Record<string, number> = {}
        for (const e of events.data) {
            if (e.location_id) {
                eventsByLocation[e.location_id] = (eventsByLocation[e.location_id] ?? 0) + 1
            }
        }
        const maxCount = Math.max(...Object.values(eventsByLocation), 1)
        for (const loc of locations.data) {
            const count = eventsByLocation[loc.id] ?? 0
            if (count > 0) {
                heatmapPoints.push([loc.lat, loc.lng, count / maxCount])
            }
        }
    }

    const getThreatColor = (loc: Location): string => {
        switch (loc.threat_level) {
            case 'red': return '#ef4444'
            case 'amber': return '#f59e0b'
            default: return '#22c55e'
        }
    }

    return (
        <Layout>
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-black text-slate-100">Synthetic Location Map</h1>
                    <p className="text-slate-500 text-sm mt-1">
                        {locations.data?.length ?? '…'} synthetic locations · {events.data?.length ?? '…'} events
                    </p>
                </div>
                {/* View toggle */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setViewMode('pins')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'pins'
                                ? 'bg-violet-600 text-white'
                                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                            }`}
                    >
                        📍 Pins View
                    </button>
                    <button
                        onClick={() => setViewMode('heatmap')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'heatmap'
                                ? 'bg-violet-600 text-white'
                                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                            }`}
                    >
                        🌡️ Heatmap View
                    </button>
                </div>
            </div>

            <ErrorMessage message={locations.error ?? events.error} />

            {locations.loading && <LoadingSpinner />}

            {locations.data && !locations.loading && (
                <>
                    {viewMode === 'heatmap' && (
                        <div className="mb-3 flex items-center gap-4 text-xs text-slate-500">
                            <span className="flex items-center gap-1">
                                <span className="w-3 h-3 rounded-full bg-blue-600 inline-block" /> Low activity
                            </span>
                            <span className="flex items-center gap-1">
                                <span className="w-3 h-3 rounded-full bg-amber-500 inline-block" /> Medium activity
                            </span>
                            <span className="flex items-center gap-1">
                                <span className="w-3 h-3 rounded-full bg-red-500 inline-block" /> High activity
                            </span>
                            <span className="ml-auto">{heatmapPoints.length} locations with events</span>
                        </div>
                    )}
                    <div className="rounded-xl overflow-hidden border border-slate-800" style={{ height: 540 }}>
                        <MapContainer
                            center={center}
                            zoom={11}
                            style={{ height: '100%', width: '100%' }}
                        >
                            <TileLayer
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                attribution='&copy; OpenStreetMap contributors'
                            />

                            {/* Heatmap layer */}
                            {viewMode === 'heatmap' && <HeatmapLayer points={heatmapPoints} />}

                            {/* Pin markers (only in pins view) */}
                            {viewMode === 'pins' && locations.data.map((loc) => {
                                const eventsHere = events.data?.filter((e) => e.location_id === loc.id) ?? []
                                return (
                                    <Marker key={loc.id} position={[loc.lat, loc.lng]}>
                                        <Popup>
                                            <div style={{ minWidth: 220, background: '#1e293b', color: '#e2e8f0', borderRadius: 8, padding: 12 }}>
                                                <p className="font-semibold text-sm">{loc.fake_address}</p>
                                                <p className="text-xs text-slate-400 mt-1">{loc.location_type}</p>
                                                {loc.district && (
                                                    <p className="text-xs text-violet-400 mt-1">📍 {loc.district}</p>
                                                )}
                                                {loc.threat_level && (
                                                    <p className="text-xs mt-1" style={{ color: getThreatColor(loc) }}>
                                                        ⚠️ {loc.threat_level.toUpperCase()} threat
                                                    </p>
                                                )}
                                                {loc.surveillance_coverage && (
                                                    <p className="text-xs text-sky-400 mt-1">📡 Under surveillance</p>
                                                )}
                                                <p className="text-xs text-slate-500 mt-2">
                                                    {eventsHere.length} event{eventsHere.length !== 1 ? 's' : ''} at this location
                                                </p>
                                                {eventsHere.slice(0, 3).map((ev) => (
                                                    <div key={ev.id} className="mt-1">
                                                        <Badge label={ev.event_type} />
                                                    </div>
                                                ))}
                                            </div>
                                        </Popup>
                                    </Marker>
                                )
                            })}
                        </MapContainer>
                    </div>
                </>
            )}
        </Layout>
    )
}
