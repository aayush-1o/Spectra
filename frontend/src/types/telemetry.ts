/**
 * Spectra — Telemetry Types  (Phase 9)
 * TypeScript interfaces for synthetic asset tracking.
 * ⚠️ 100% synthetic data — no real aircraft or vehicles.
 */

export type AssetType = 'drone' | 'flight' | 'vehicle'

/** One asset's current geographic position, received from the WebSocket. */
export interface AssetPosition {
    id: string
    label: string
    asset_type: AssetType
    lat: number
    lon: number
    altitude_m: number
    heading: number   // 0–360 degrees
    speed_kmh: number
    timestamp: number   // Unix epoch seconds
}

/** A lightweight description of an asset, sent once in the manifest frame. */
export interface AssetManifest {
    id: string
    label: string
    asset_type: AssetType
}

/** WebSocket message types */
export interface ManifestFrame {
    type: 'manifest'
    synthetic: boolean
    ethics: string
    assets: AssetManifest[]
}

export interface PositionsFrame {
    type: 'positions'
    data: AssetPosition[]
}

export type TelemetryFrame = ManifestFrame | PositionsFrame

/**
 * A historical snapshot entry: positions keyed by asset id at a given timestamp.
 * Used by the time scrubber to replay past positions.
 */
export interface HistoryEntry {
    timestamp: number
    positions: Record<string, AssetPosition>
}
