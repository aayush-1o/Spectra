/**
 * Spectra — Asset Tracking Page  (Phase 10, CesiumJS 3D Globe)
 *
 * Globe: Resium (React wrapper for CesiumJS)
 *        — 3D Earth, satellite imagery via Cesium Ion
 *        — Falls back to OpenStreetMap tiles if no Ion token
 * HUD:   Pure HTML/CSS overlay above the canvas — NOT inside Cesium
 * Modes: CSS filter classes (Normal / Night Vision / Thermal / Tactical)
 * Visual: Auto-rotation, pulsing rings overlay, glow trails
 *
 * ⚠️ ALL DATA IS 100% SYNTHETIC — no real aircraft, drones, or vehicles.
 */

import {
    useState,
    useMemo,
    useCallback,
    useRef,
    useEffect,
} from 'react'
import {
    Viewer,
    CameraFlyTo,
    BillboardCollection,
    Billboard,
    PolylineCollection,
    Polyline,
} from 'resium'
import * as Cesium from 'cesium'
import EthicsBanner from '../components/layout/EthicsBanner'
import Sidebar from '../components/layout/Sidebar'
import TimeScrubber from '../components/map/TimeScrubber'
import { useAssetStream } from '../hooks/useAssetStream'
import type { AssetPosition, HistoryEntry } from '../types/telemetry'

// ── Ion token ─────────────────────────────────────────────────────────────────
const ION_TOKEN = import.meta.env.VITE_CESIUM_TOKEN as string | undefined
if (ION_TOKEN) {
    Cesium.Ion.defaultAccessToken = ION_TOKEN
}

// ── WebSocket URL ─────────────────────────────────────────────────────────────
const WS_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000')
    .replace(/^http/, 'ws').replace(/\/$/, '') + '/api/v1/stream/assets'

// ── Trail config ──────────────────────────────────────────────────────────────
const TRAIL_LENGTH = 20

// ── Type colours ──────────────────────────────────────────────────────────────
function typeColorCesium(type: string): Cesium.Color {
    switch (type) {
        case 'flight': return Cesium.Color.fromCssColorString('#3b82f6').withAlpha(0.95)
        case 'drone': return Cesium.Color.fromCssColorString('#a855f7').withAlpha(0.95)
        case 'vehicle': return Cesium.Color.fromCssColorString('#10b981').withAlpha(0.95)
        default: return Cesium.Color.fromCssColorString('#64748b').withAlpha(0.8)
    }
}
function typeColorHex(type: string): string {
    switch (type) {
        case 'flight': return '#3b82f6'
        case 'drone': return '#a855f7'
        case 'vehicle': return '#10b981'
        default: return '#64748b'
    }
}
function typeColorTrail(type: string): Cesium.Color {
    return typeColorCesium(type).withAlpha(0.45)
}

// ── Altitude helpers ──────────────────────────────────────────────────────────
function renderAltitude(pos: AssetPosition): number {
    switch (pos.asset_type) {
        case 'flight': return Math.max(pos.altitude_m, 3000)
        case 'drone': return Math.max(pos.altitude_m, 50)
        case 'vehicle': return 0
        default: return pos.altitude_m
    }
}

// ── Billboard SVG icons (data URIs) ──────────────────────────────────────────
function makeBillboard(type: string): string {
    const color = { flight: '#3b82f6', drone: '#a855f7', vehicle: '#10b981' }[type] ?? '#94a3b8'
    const light = { flight: '#93c5fd', drone: '#d8b4fe', vehicle: '#6ee7b7' }[type] ?? '#cbd5e1'
    let inner = ''
    if (type === 'flight') {
        inner = `
          <polygon points="32,6 38,28 54,33 38,36 36,58 32,52 28,58 26,36 10,33 26,28" fill="${color}"/>
          <polygon points="32,6 38,28 54,33 26,28" fill="${light}"/>
          <circle cx="32" cy="24" r="3.5" fill="white" fill-opacity=".85"/>`
    } else if (type === 'drone') {
        inner = `
          <circle cx="32" cy="32" r="12" fill="${color}"/>
          <line x1="22" y1="22" x2="12" y2="12" stroke="${color}" stroke-width="3.5" stroke-linecap="round"/>
          <line x1="42" y1="22" x2="52" y2="12" stroke="${color}" stroke-width="3.5" stroke-linecap="round"/>
          <line x1="22" y1="42" x2="12" y2="52" stroke="${color}" stroke-width="3.5" stroke-linecap="round"/>
          <line x1="42" y1="42" x2="52" y2="52" stroke="${color}" stroke-width="3.5" stroke-linecap="round"/>
          <circle cx="11" cy="11" r="5.5" fill="${light}"/>
          <circle cx="53" cy="11" r="5.5" fill="${light}"/>
          <circle cx="11" cy="53" r="5.5" fill="${light}"/>
          <circle cx="53" cy="53" r="5.5" fill="${light}"/>
          <circle cx="32" cy="32" r="4.5" fill="white" fill-opacity=".9"/>`
    } else {
        inner = `
          <rect x="17" y="18" width="30" height="36" rx="6" fill="${color}"/>
          <rect x="20" y="21" width="24" height="15" rx="3" fill="${light}"/>
          <circle cx="20" cy="19" r="4.5" fill="#0f172a"/>
          <circle cx="44" cy="19" r="4.5" fill="#0f172a"/>
          <circle cx="20" cy="55" r="4.5" fill="#0f172a"/>
          <circle cx="44" cy="55" r="4.5" fill="#0f172a"/>
          <rect x="25" y="37" width="14" height="4" rx="1.5" fill="${light}" fill-opacity=".7"/>`
    }
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">${inner}</svg>`
    return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

const BILLBOARD_URLS: Record<string, string> = {
    flight: makeBillboard('flight'),
    drone: makeBillboard('drone'),
    vehicle: makeBillboard('vehicle'),
}

// ── Visual modes ───────────────────────────────────────────────────────────────
type ViewMode = 'normal' | 'nightvision' | 'thermal' | 'tactical'

const MODE_FILTERS: Record<ViewMode, string> = {
    normal: 'none',
    nightvision: 'brightness(0.65) hue-rotate(88deg) saturate(4) sepia(0.55)',
    thermal: 'brightness(0.8) sepia(1) saturate(6) hue-rotate(-28deg)',
    tactical: 'brightness(0.45) saturate(0.15) contrast(1.5)',
}

const MODE_LABELS: Record<ViewMode, string> = {
    normal: '🌍 Normal',
    nightvision: '🟢 Night Vision',
    thermal: '🔴 Thermal',
    tactical: '⬛ Tactical',
}

// ── UTC Clock ─────────────────────────────────────────────────────────────────
function useUtcClock() {
    const [time, setTime] = useState(() => new Date().toUTCString().slice(17, 25))
    useEffect(() => {
        const id = setInterval(() => {
            setTime(new Date().toUTCString().slice(17, 25))
        }, 1000)
        return () => clearInterval(id)
    }, [])
    return time
}

// ── Cursor coordinates ─────────────────────────────────────────────────────────
function useCursorCoords(viewerRef: React.RefObject<Cesium.Viewer | null>) {
    const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null)
    useEffect(() => {
        const viewer = viewerRef.current
        if (!viewer) return
        const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
        handler.setInputAction((movement: Cesium.ScreenSpaceEventHandler.MotionEvent) => {
            const cartesian = viewer.camera.pickEllipsoid(
                movement.endPosition,
                Cesium.Ellipsoid.WGS84
            )
            if (cartesian) {
                const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian)
                setCoords({
                    lat: Cesium.Math.toDegrees(carto.latitude),
                    lon: Cesium.Math.toDegrees(carto.longitude),
                })
            }
        }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
        return () => handler.destroy()
    }, [viewerRef])
    return coords
}

// ── Globe auto-rotation ────────────────────────────────────────────────────────
// Slowly rotates the camera around the globe's Z axis when idle (no selection)
function useGlobeAutoRotation(
    viewerRef: React.RefObject<Cesium.Viewer | null>,
    paused: boolean,
) {
    useEffect(() => {
        const RATE = 0.04 // degrees per tick (~60 ticks/s → ~2.4 deg/s → full lap ~150s)
        const id = setInterval(() => {
            if (paused) return
            const viewer = viewerRef.current
            if (!viewer || viewer.isDestroyed()) return
            viewer.scene.camera.rotate(
                Cesium.Cartesian3.UNIT_Z,
                Cesium.Math.toRadians(RATE),
            )
        }, 16) // ~60 fps
        return () => clearInterval(id)
    }, [viewerRef, paused])
}

// ── Pulsing rings canvas overlay ───────────────────────────────────────────────
// Draws animated concentric rings around each asset icon on a 2D overlay canvas
function PulsingRingsOverlay({
    viewerRef,
    positions,
}: {
    viewerRef: React.RefObject<Cesium.Viewer | null>
    positions: Array<{ id: string; lat: number; lon: number; alt: number; type: string }>
}) {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const frameRef = useRef<number>(0)
    const startRef = useRef<number>(Date.now())

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return
        const ctx = canvas.getContext('2d')!

        const TYPE_COLORS: Record<string, string> = {
            flight: '59,130,246',
            drone: '168,85,247',
            vehicle: '16,185,129',
        }

        const draw = () => {
            const viewer = viewerRef.current
            if (!viewer || viewer.isDestroyed()) {
                frameRef.current = requestAnimationFrame(draw)
                return
            }

            // Sync canvas size to container
            const parent = canvas.parentElement!
            if (canvas.width !== parent.clientWidth) canvas.width = parent.clientWidth
            if (canvas.height !== parent.clientHeight) canvas.height = parent.clientHeight

            ctx.clearRect(0, 0, canvas.width, canvas.height)

            const elapsed = (Date.now() - startRef.current) / 1000 // seconds

            for (const pos of positions) {
                const cartesian = Cesium.Cartesian3.fromDegrees(pos.lon, pos.lat, pos.alt)
                const windowCoord = Cesium.SceneTransforms.worldToWindowCoordinates(
                    viewer.scene,
                    cartesian,
                )
                if (!windowCoord) continue

                const { x, y } = windowCoord
                const rgb = TYPE_COLORS[pos.type] ?? '148,163,184'

                // Draw 2 concentric pulsing rings per asset
                for (let ring = 0; ring < 2; ring++) {
                    // Each ring is offset in phase so they expand outward in sequence
                    const phase = (elapsed * 0.8 + ring * 0.5) % 1.0
                    const radius = 14 + phase * 28
                    const alpha = (1 - phase) * (pos.type === 'flight' ? 0.7 : 0.55)

                    ctx.beginPath()
                    ctx.arc(x, y, radius, 0, Math.PI * 2)
                    ctx.strokeStyle = `rgba(${rgb},${alpha.toFixed(2)})`
                    ctx.lineWidth = pos.type === 'flight' ? 1.5 : 1.2
                    ctx.stroke()
                }

                // Inner glow dot
                const gDot = ctx.createRadialGradient(x, y, 0, x, y, 10)
                gDot.addColorStop(0, `rgba(${rgb},0.45)`)
                gDot.addColorStop(1, `rgba(${rgb},0)`)
                ctx.beginPath()
                ctx.arc(x, y, 10, 0, Math.PI * 2)
                ctx.fillStyle = gDot
                ctx.fill()
            }

            frameRef.current = requestAnimationFrame(draw)
        }

        frameRef.current = requestAnimationFrame(draw)
        return () => cancelAnimationFrame(frameRef.current)
    }, [viewerRef, positions])

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'absolute',
                inset: 0,
                pointerEvents: 'none',
                zIndex: 6,
            }}
        />
    )
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function AssetTrackingPage() {
    const { assetList, manifest, connected, error, history } = useAssetStream(WS_URL)
    const [selected, setSelected] = useState<AssetPosition | null>(null)
    const [scrubEntry, setScrubEntry] = useState<HistoryEntry | null>(null)
    const [viewMode, setViewMode] = useState<ViewMode>('normal')
    const [flyTarget] = useState({
        destination: Cesium.Cartesian3.fromDegrees(0, 20, 20_000_000),
        orientation: { heading: 0, pitch: -Math.PI / 2, roll: 0 },
    })
    const isLive = scrubEntry === null
    const viewerRef = useRef<Cesium.Viewer | null>(null)
    const utcTime = useUtcClock()
    const cursorCoords = useCursorCoords(viewerRef)

    // Auto-rotation: paused when an asset is selected or user is scrubbing
    useGlobeAutoRotation(viewerRef, selected !== null || !isLive)

    // Trail ref
    const trailRef = useRef<Record<string, [number, number, number][]>>({})
    if (isLive) {
        for (const pos of assetList) {
            const trail = trailRef.current[pos.id] ?? []
            trail.push([pos.lon, pos.lat, renderAltitude(pos)])
            if (trail.length > TRAIL_LENGTH) trail.shift()
            trailRef.current[pos.id] = trail
        }
    }

    const displayPositions: AssetPosition[] = useMemo(() => {
        if (!isLive && scrubEntry) return Object.values(scrubEntry.positions)
        return assetList
    }, [isLive, scrubEntry, assetList])

    // Pulsing rings data — derived from display positions (must be after displayPositions)
    const ringPositions = useMemo(() =>
        displayPositions.map(pos => ({
            id: pos.id,
            lat: pos.lat,
            lon: pos.lon,
            alt: renderAltitude(pos),
            type: pos.asset_type,
        })),
        [displayPositions]
    )

    const counts = useMemo(() => ({
        drone: displayPositions.filter(p => p.asset_type === 'drone').length,
        flight: displayPositions.filter(p => p.asset_type === 'flight').length,
        vehicle: displayPositions.filter(p => p.asset_type === 'vehicle').length,
    }), [displayPositions])

    // Build Cesium cartesian positions for billboards
    const billboardData = useMemo(() =>
        displayPositions.map(pos => ({
            pos,
            cartesian: Cesium.Cartesian3.fromDegrees(pos.lon, pos.lat, renderAltitude(pos)),
        })),
        [displayPositions])

    // Build trail polyline data
    const trailData = useMemo(() => {
        if (!isLive && scrubEntry) return []
        return Object.entries(trailRef.current)
            .filter(([, path]) => path.length >= 2)
            .map(([id, path]) => {
                const ma = manifest.find(m => m.id === id)
                const type = ma?.asset_type ?? 'vehicle'
                const positions = path.map(([lon, lat, alt]) =>
                    Cesium.Cartesian3.fromDegrees(lon, lat, alt)
                )
                return { positions, color: typeColorTrail(type) }
            })
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isLive, scrubEntry, manifest, displayPositions.length])

    const handleBillboardClick = useCallback((pos: AssetPosition) => {
        setSelected(prev => prev?.id === pos.id ? null : pos)
    }, [])

    // Set viewer ref from resium
    const handleRef = useCallback((v: { cesiumElement: Cesium.Viewer } | null) => {
        if (v?.cesiumElement) {
            viewerRef.current = v.cesiumElement
        }
    }, [])

    return (
        <div style={{
            display: 'flex', flexDirection: 'column', height: '100vh',
            background: '#050810', fontFamily: 'Inter, system-ui, sans-serif',
            overflow: 'hidden',
        }}>
            <EthicsBanner />

            <div style={{ display: 'flex', flex: 1, marginTop: 'var(--ethics-banner-height)', overflow: 'hidden' }}>
                <Sidebar />

                {/* ── Viewport ─────────────────────────────────────────── */}
                <div style={{ position: 'relative', flex: 1, overflow: 'hidden' }}>

                    {/* Globe with CSS mode filter applied */}
                    <div style={{
                        position: 'absolute', inset: 0,
                        filter: MODE_FILTERS[viewMode],
                        transition: 'filter 0.6s ease',
                    }}>
                        <Viewer
                            ref={handleRef}
                            full
                            animation={false}
                            baseLayerPicker={false}
                            fullscreenButton={false}
                            geocoder={false}
                            homeButton={false}
                            infoBox={false}
                            navigationHelpButton={false}
                            sceneModePicker={false}
                            selectionIndicator={false}
                            timeline={false}
                            style={{ width: '100%', height: '100%' }}
                        >
                            {/* Initial camera position — looking down at Earth */}
                            <CameraFlyTo
                                destination={flyTarget.destination}
                                orientation={flyTarget.orientation}
                                duration={0}
                            />

                            {/* Trails — enhanced glow */}
                            <PolylineCollection>
                                {trailData.map((trail, i) => (
                                    <Polyline
                                        key={i}
                                        positions={trail.positions}
                                        material={new Cesium.PolylineGlowMaterialProperty({
                                            glowPower: 0.35,
                                            color: trail.color,
                                        }) as unknown as Cesium.Material}
                                        width={3}
                                    />
                                ))}
                            </PolylineCollection>

                            {/* Asset billboards */}
                            <BillboardCollection>
                                {billboardData.map(({ pos, cartesian }) => (
                                    <Billboard
                                        key={pos.id}
                                        position={cartesian}
                                        image={BILLBOARD_URLS[pos.asset_type] ?? BILLBOARD_URLS['vehicle']}
                                        scale={pos.asset_type === 'flight' ? 1.1 : 0.85}
                                        verticalOrigin={Cesium.VerticalOrigin.CENTER}
                                        horizontalOrigin={Cesium.HorizontalOrigin.CENTER}
                                        color={typeColorCesium(pos.asset_type)}
                                        onClick={() => handleBillboardClick(pos)}
                                        pixelOffset={new Cesium.Cartesian2(0, 0)}
                                        eyeOffset={new Cesium.Cartesian3(0, 0, -1000)}
                                        heightReference={
                                            pos.asset_type === 'vehicle'
                                                ? Cesium.HeightReference.CLAMP_TO_GROUND
                                                : Cesium.HeightReference.NONE
                                        }
                                        disableDepthTestDistance={Number.POSITIVE_INFINITY}
                                        id={pos.id}
                                    />
                                ))}
                            </BillboardCollection>
                        </Viewer>
                    </div>

                    {/* ── Pulsing rings canvas overlay ─────────────────── */}
                    <PulsingRingsOverlay
                        viewerRef={viewerRef}
                        positions={ringPositions}
                    />

                    {/* ── Tactical grid overlay ───────────────────────── */}
                    {viewMode === 'tactical' && (
                        <div style={{
                            position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 5,
                            backgroundImage: `
                                linear-gradient(rgba(0,255,80,0.07) 1px, transparent 1px),
                                linear-gradient(90deg, rgba(0,255,80,0.07) 1px, transparent 1px)
                            `,
                            backgroundSize: '60px 60px',
                        }} />
                    )}

                    {/* ── Night vision scanline overlay ───────────────── */}
                    {viewMode === 'nightvision' && (
                        <div style={{
                            position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 5,
                            backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px, transparent 1px, transparent 3px)',
                        }} />
                    )}

                    {/* ══════════════════════════════════════════════════
                        HUD — all elements are HTML above the canvas
                    ══════════════════════════════════════════════════ */}

                    {/* ── Top classification banner ───────────────────── */}
                    <div style={{
                        position: 'absolute', top: 0, left: 0, right: 0,
                        background: 'rgba(220,38,38,0.92)',
                        borderBottom: '1px solid rgba(239,68,68,0.5)',
                        padding: '3px 0',
                        textAlign: 'center',
                        fontSize: 10, fontWeight: 700, letterSpacing: '0.18em',
                        color: '#fff', zIndex: 1000,
                        fontFamily: "'JetBrains Mono', monospace",
                        textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                    }}>
                        TS // SI-TK // NOFORN — &nbsp;SYNTHETIC DATA ONLY — NOT REAL SURVEILLANCE
                    </div>

                    {/* ── Top-left: Logo + connection status ───────────── */}
                    <div style={{
                        position: 'absolute', top: 28, left: 12, zIndex: 900,
                        display: 'flex', flexDirection: 'column', gap: 6,
                    }}>
                        <div style={{
                            background: 'rgba(2,6,23,0.88)',
                            border: '1px solid rgba(59,130,246,0.35)',
                            borderRadius: 6,
                            padding: '8px 14px',
                            backdropFilter: 'blur(12px)',
                            display: 'flex', alignItems: 'center', gap: 12,
                        }}>
                            {/* Logo */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <span style={{
                                    fontSize: 18, fontWeight: 800, letterSpacing: '0.1em',
                                    color: '#e2e8f0', fontFamily: 'Inter, sans-serif',
                                    lineHeight: 1,
                                }}>SPECTRA</span>
                                <span style={{
                                    fontSize: 8.5, fontWeight: 600, letterSpacing: '0.2em',
                                    color: '#3b82f6', fontFamily: "'JetBrains Mono', monospace",
                                }}>INTELLIGENCE PLATFORM</span>
                            </div>

                            <div style={{ width: 1, height: 28, background: 'rgba(148,163,184,0.2)' }} />

                            {/* Connection pill */}
                            <div style={{
                                display: 'flex', alignItems: 'center', gap: 6,
                                padding: '4px 10px', borderRadius: 20,
                                background: connected ? 'rgba(21,128,61,0.3)' : 'rgba(185,28,28,0.3)',
                                border: `1px solid ${connected ? 'rgba(34,197,94,0.4)' : 'rgba(239,68,68,0.4)'}`,
                            }}>
                                <span style={{
                                    width: 6, height: 6, borderRadius: '50%',
                                    background: connected ? '#22c55e' : '#ef4444',
                                    boxShadow: connected ? '0 0 6px #22c55e' : '0 0 6px #ef4444',
                                }} />
                                <span style={{
                                    fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
                                    color: connected ? '#4ade80' : '#f87171',
                                    fontFamily: "'JetBrains Mono', monospace",
                                }}>
                                    {connected ? 'LIVE FEED' : 'OFFLINE'}
                                </span>
                            </div>

                            {!isLive && (
                                <div style={{
                                    padding: '4px 10px', borderRadius: 20,
                                    background: 'rgba(146,64,14,0.3)',
                                    border: '1px solid rgba(251,191,36,0.4)',
                                    fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
                                    color: '#fbbf24', fontFamily: "'JetBrains Mono', monospace",
                                }}>
                                    ⏪ REPLAY
                                </div>
                            )}
                        </div>

                        {/* Asset count badges */}
                        <div style={{ display: 'flex', gap: 6 }}>
                            {[
                                { type: 'flight', count: counts.flight, label: 'FLIGHTS', color: '#3b82f6' },
                                { type: 'drone', count: counts.drone, label: 'DRONES', color: '#a855f7' },
                                { type: 'vehicle', count: counts.vehicle, label: 'VEHICLES', color: '#10b981' },
                            ].map(({ count, label, color }) => (
                                <div key={label} style={{
                                    background: 'rgba(2,6,23,0.85)',
                                    border: `1px solid ${color}44`,
                                    borderRadius: 5,
                                    padding: '4px 10px',
                                    backdropFilter: 'blur(8px)',
                                    textAlign: 'center',
                                }}>
                                    <div style={{
                                        fontSize: 17, fontWeight: 700,
                                        color, fontFamily: "'JetBrains Mono', monospace",
                                        lineHeight: 1,
                                    }}>{count}</div>
                                    <div style={{ fontSize: 8, color: '#94a3b8', letterSpacing: '0.12em', marginTop: 2 }}>{label}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* ── Top-right: UTC clock + cursor coords ─────────── */}
                    <div style={{
                        position: 'absolute', top: 28, right: 12, zIndex: 900,
                        display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end',
                    }}>
                        <div style={{
                            background: 'rgba(2,6,23,0.88)',
                            border: '1px solid rgba(59,130,246,0.25)',
                            borderRadius: 6, padding: '8px 14px',
                            backdropFilter: 'blur(12px)',
                            display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 3,
                        }}>
                            <div style={{
                                fontSize: 9, fontWeight: 600, letterSpacing: '0.16em',
                                color: '#64748b', fontFamily: "'JetBrains Mono', monospace",
                            }}>ZULU TIME</div>
                            <div style={{
                                fontSize: 22, fontWeight: 700, letterSpacing: '0.05em',
                                color: '#e2e8f0', fontFamily: "'JetBrains Mono', monospace",
                                lineHeight: 1,
                            }}>{utcTime}Z</div>
                        </div>

                        {cursorCoords && (
                            <div style={{
                                background: 'rgba(2,6,23,0.85)',
                                border: '1px solid rgba(148,163,184,0.2)',
                                borderRadius: 5, padding: '6px 12px',
                                backdropFilter: 'blur(8px)',
                            }}>
                                <div style={{
                                    fontSize: 11, fontFamily: "'JetBrains Mono', monospace",
                                    color: '#94a3b8', letterSpacing: '0.05em',
                                }}>
                                    {cursorCoords.lat.toFixed(4)}°{cursorCoords.lat >= 0 ? 'N' : 'S'}
                                    &nbsp;
                                    {Math.abs(cursorCoords.lon).toFixed(4)}°{cursorCoords.lon >= 0 ? 'E' : 'W'}
                                </div>
                            </div>
                        )}

                        {/* Visual mode toggles */}
                        <div style={{
                            background: 'rgba(2,6,23,0.85)',
                            border: '1px solid rgba(148,163,184,0.15)',
                            borderRadius: 6, padding: '6px 8px',
                            backdropFilter: 'blur(8px)',
                            display: 'flex', gap: 5,
                        }}>
                            {(Object.keys(MODE_LABELS) as ViewMode[]).map(mode => (
                                <button
                                    key={mode}
                                    onClick={() => setViewMode(mode)}
                                    style={{
                                        padding: '5px 10px', borderRadius: 4,
                                        fontSize: 10.5, fontWeight: 600, cursor: 'pointer',
                                        letterSpacing: '0.04em',
                                        background: viewMode === mode ? 'rgba(59,130,246,0.25)' : 'transparent',
                                        border: `1px solid ${viewMode === mode ? '#3b82f6' : 'rgba(148,163,184,0.2)'}`,
                                        color: viewMode === mode ? '#93c5fd' : '#64748b',
                                        transition: 'all 0.15s',
                                        fontFamily: 'Inter, sans-serif',
                                    }}
                                >
                                    {MODE_LABELS[mode]}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* ── Error banner ────────────────────────────────── */}
                    {error && (
                        <div style={{
                            position: 'absolute', top: 130, left: 12, right: 12,
                            zIndex: 901,
                            background: 'rgba(127,29,29,0.9)',
                            border: '1px solid rgba(239,68,68,0.4)',
                            borderRadius: 5,
                            color: '#fca5a5', padding: '8px 14px', fontSize: 12,
                            fontFamily: "'JetBrains Mono', monospace",
                        }}>
                            ⚠ {error}
                        </div>
                    )}

                    {/* ── Asset list (left panel) ──────────────────────── */}
                    <div style={{
                        position: 'absolute', top: 176, left: 12, bottom: 64,
                        width: 220, overflowY: 'auto', zIndex: 900,
                        background: 'rgba(2,6,23,0.88)',
                        border: '1px solid rgba(148,163,184,0.15)',
                        borderRadius: 8,
                        backdropFilter: 'blur(12px)',
                        display: 'flex', flexDirection: 'column',
                    }}>
                        {/* Panel header */}
                        <div style={{
                            padding: '9px 13px',
                            borderBottom: '1px solid rgba(148,163,184,0.12)',
                            fontSize: 9.5, fontWeight: 700, letterSpacing: '0.18em',
                            color: '#475569',
                            fontFamily: "'JetBrains Mono', monospace",
                            flexShrink: 0,
                        }}>
                            TRACKED ASSETS ({displayPositions.length})
                        </div>

                        <div style={{ overflowY: 'auto', flex: 1 }}>
                            {displayPositions.length === 0 ? (
                                <div style={{
                                    padding: '20px 13px', fontSize: 11,
                                    color: '#334155', textAlign: 'center',
                                    fontFamily: "'JetBrains Mono', monospace",
                                }}>
                                    Waiting for data…
                                </div>
                            ) : (
                                displayPositions.map(pos => {
                                    const isSelected = selected?.id === pos.id
                                    const hex = typeColorHex(pos.asset_type)
                                    return (
                                        <div
                                            key={pos.id}
                                            onClick={() => setSelected(prev => prev?.id === pos.id ? null : pos)}
                                            style={{
                                                padding: '9px 13px', cursor: 'pointer',
                                                borderBottom: '1px solid rgba(148,163,184,0.07)',
                                                borderLeft: `3px solid ${isSelected ? hex : 'transparent'}`,
                                                background: isSelected ? `${hex}18` : 'transparent',
                                                display: 'flex', alignItems: 'center', gap: 9,
                                                transition: 'all 0.1s',
                                            }}
                                        >
                                            {/* Type dot */}
                                            <div style={{
                                                width: 8, height: 8, borderRadius: '50%',
                                                background: hex, flexShrink: 0,
                                                boxShadow: `0 0 5px ${hex}`,
                                            }} />
                                            <div style={{ flex: 1, overflow: 'hidden' }}>
                                                {/* Label */}
                                                <div style={{
                                                    fontSize: 12, fontWeight: 600,
                                                    fontFamily: "'JetBrains Mono', monospace",
                                                    color: isSelected ? '#e2e8f0' : '#94a3b8',
                                                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                                                    letterSpacing: '0.02em',
                                                }}>
                                                    {pos.label}
                                                </div>
                                                {/* Sub-row */}
                                                <div style={{
                                                    fontSize: 10.5, color: '#475569',
                                                    fontFamily: "'JetBrains Mono', monospace",
                                                    marginTop: 2, display: 'flex', gap: 6,
                                                }}>
                                                    <span>{pos.speed_kmh.toFixed(0)}&thinsp;km/h</span>
                                                    <span style={{ color: '#334155' }}>·</span>
                                                    <span>{renderAltitude(pos).toFixed(0)}&thinsp;m</span>
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })
                            )}
                        </div>
                    </div>

                    {/* ── Selected asset detail panel (right) ─────────── */}
                    {selected && (
                        <div style={{
                            position: 'absolute', top: 176, right: 12,
                            width: 268, zIndex: 950,
                            background: 'rgba(2,6,23,0.92)',
                            border: `1px solid ${typeColorHex(selected.asset_type)}55`,
                            borderRadius: 8,
                            backdropFilter: 'blur(16px)',
                            overflow: 'hidden',
                        }}>
                            {/* Header */}
                            <div style={{
                                padding: '11px 14px 10px',
                                borderBottom: `1px solid ${typeColorHex(selected.asset_type)}30`,
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            }}>
                                <div>
                                    <div style={{
                                        fontSize: 14, fontWeight: 700,
                                        fontFamily: "'JetBrains Mono', monospace",
                                        color: '#e2e8f0', letterSpacing: '0.04em',
                                    }}>
                                        {selected.label}
                                    </div>
                                    <div style={{
                                        fontSize: 9, fontWeight: 600, letterSpacing: '0.18em',
                                        textTransform: 'uppercase',
                                        color: typeColorHex(selected.asset_type),
                                        marginTop: 3,
                                    }}>
                                        {selected.asset_type} · ID {selected.id.slice(0, 8)}
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSelected(null)}
                                    style={{
                                        background: 'rgba(148,163,184,0.1)',
                                        border: '1px solid rgba(148,163,184,0.2)',
                                        borderRadius: 4, width: 26, height: 26,
                                        cursor: 'pointer', color: '#64748b',
                                        fontSize: 15, display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    }}
                                >×</button>
                            </div>

                            {/* Telemetry rows */}
                            {([
                                ['LAT', `${selected.lat.toFixed(5)}°`],
                                ['LON', `${selected.lon.toFixed(5)}°`],
                                ['ALT', `${renderAltitude(selected).toLocaleString()} m`],
                                ['HEADING', `${selected.heading.toFixed(1)}°`],
                                ['SPEED', `${selected.speed_kmh.toFixed(0)} km/h`],
                            ] as [string, string][]).map(([k, v]) => (
                                <div key={k} style={{
                                    display: 'flex', justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '9px 14px',
                                    borderBottom: '1px solid rgba(148,163,184,0.07)',
                                }}>
                                    <span style={{
                                        fontSize: 9.5, fontWeight: 600, letterSpacing: '0.14em',
                                        color: '#475569', fontFamily: "'JetBrains Mono', monospace",
                                    }}>{k}</span>
                                    <span style={{
                                        fontSize: 13, fontWeight: 500,
                                        color: '#e2e8f0', fontFamily: "'JetBrains Mono', monospace",
                                        letterSpacing: '0.03em',
                                    }}>{v}</span>
                                </div>
                            ))}

                            <div style={{
                                padding: '8px 14px', fontSize: 9,
                                color: '#334155', textAlign: 'center',
                                fontFamily: "'JetBrains Mono', monospace",
                                letterSpacing: '0.1em',
                            }}>
                                ⚠ SYNTHETIC DATA — NOT A REAL {selected.asset_type.toUpperCase()}
                            </div>
                        </div>
                    )}

                    {/* ── Legend (bottom-left, above scrubber) ─────────── */}
                    <div style={{
                        position: 'absolute', bottom: 66, left: 244, zIndex: 900,
                        background: 'rgba(2,6,23,0.85)',
                        border: '1px solid rgba(148,163,184,0.12)',
                        borderRadius: 5, padding: '7px 12px',
                        backdropFilter: 'blur(10px)',
                        display: 'flex', gap: 14, alignItems: 'center',
                    }}>
                        {[
                            { color: '#3b82f6', label: 'FLIGHT' },
                            { color: '#a855f7', label: 'DRONE' },
                            { color: '#10b981', label: 'VEHICLE' },
                        ].map(({ color, label }) => (
                            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <span style={{
                                    width: 7, height: 7, borderRadius: '50%',
                                    background: color, boxShadow: `0 0 5px ${color}`,
                                    flexShrink: 0,
                                }} />
                                <span style={{
                                    fontSize: 9.5, fontWeight: 600, color: '#64748b',
                                    letterSpacing: '0.12em',
                                    fontFamily: "'JetBrains Mono', monospace",
                                }}>{label}</span>
                            </div>
                        ))}
                        <div style={{
                            width: 1, height: 14, background: 'rgba(148,163,184,0.15)',
                        }} />
                        <span style={{
                            fontSize: 8.5, color: '#334155', letterSpacing: '0.1em',
                            fontFamily: "'JetBrains Mono', monospace",
                        }}>SYNTHETIC ONLY</span>
                    </div>

                    {/* ── TimeScrubber (unchanged component) ───────────── */}
                    <TimeScrubber history={history} onScrub={setScrubEntry} isLive={isLive} />
                </div>
            </div>
        </div>
    )
}
