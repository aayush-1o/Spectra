/**
 * Spectra — Map Page
 * Renders all synthetic locations as Leaflet map markers.
 */
import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'
import { useApi } from '../hooks/useApi'
import { listLocations } from '../api/locations'
import { listEvents } from '../api/events'

// Fix Leaflet default icon paths broken by Vite bundling
// @ts-expect-error private property
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function MapPage() {
    const locations = useApi(() => listLocations({ limit: 100 }))
    const events = useApi(() => listEvents({ limit: 100 }))

    // Inject Leaflet dark tile — no extra CSS needed
    useEffect(() => {
        const style = document.createElement('style')
        style.textContent = `.leaflet-container { background: #0d1117 !important; }`
        document.head.appendChild(style)
        return () => { document.head.removeChild(style) }
    }, [])

    const center: [number, number] = locations.data?.[0]
        ? [locations.data[0].lat, locations.data[0].lng]
        : [37.7749, -122.4194]

    return (
        <Layout>
            <div className="mb-6">
                <h1 className="text-2xl font-black text-slate-100">Synthetic Location Map</h1>
                <p className="text-slate-500 text-sm mt-1">
                    {locations.data?.length ?? '…'} synthetic locations · {events.data?.length ?? '…'} events
                </p>
            </div>

            <ErrorMessage message={locations.error ?? events.error} />

            {locations.loading && <LoadingSpinner />}

            {locations.data && !locations.loading && (
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
                        {locations.data.map((loc) => {
                            const eventsHere = events.data?.filter((e) => e.location_id === loc.id) ?? []
                            return (
                                <Marker key={loc.id} position={[loc.lat, loc.lng]}>
                                    <Popup>
                                        <div style={{ minWidth: 200, background: '#1e293b', color: '#e2e8f0', borderRadius: 8, padding: 12 }}>
                                            <p className="font-semibold text-sm">{loc.fake_address}</p>
                                            <p className="text-xs text-slate-400 mt-1">{loc.location_type}</p>
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
            )}
        </Layout>
    )
}
