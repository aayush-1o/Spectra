/**
 * Spectra — Shared TypeScript Types
 * All interfaces mirror backend Pydantic schemas exactly.
 */

// ── Auth ──────────────────────────────────────────────────────────────────────
export interface LoginRequest {
    username: string
    password: string
}

export interface RegisterRequest {
    username: string
    password: string
}

export interface TokenResponse {
    access_token: string
    token_type: string
}

// ── Person ────────────────────────────────────────────────────────────────────
export interface Person {
    id: string
    fake_name: string
    date_of_birth: string
    occupation: string | null
    location_id: string | null
    metadata_: Record<string, unknown>
    created_at: string
}

// ── Location ──────────────────────────────────────────────────────────────────
export type LocationType = 'residential' | 'commercial' | 'industrial' | 'public' | 'unknown'

export interface Location {
    id: string
    fake_address: string
    lat: number
    lng: number
    location_type: LocationType
    metadata_: Record<string, unknown>
    created_at: string
}

// ── Event ─────────────────────────────────────────────────────────────────────
export type EventType = 'call' | 'message' | 'meeting' | 'transfer' | 'login'

export interface Event {
    id: string
    event_type: EventType
    actor_id: string
    target_id: string
    location_id: string | null
    occurred_at: string
    anomaly_score: number | null
    metadata_: Record<string, unknown>
    created_at: string
}

// ── Graph ─────────────────────────────────────────────────────────────────────
export interface GraphNode {
    id: string
    label: string
    properties: {
        fake_name?: string
        occupation?: string
        fake_address?: string
        location_type?: string
    }
}

export interface GraphEdge {
    source: string
    target: string
    type: string
    properties: {
        event_id?: string
        ts?: string
        amount_usd?: number
    }
}

export interface NeighbourhoodResponse {
    nodes: GraphNode[]
    edges: GraphEdge[]
}

export interface CentralityEntry {
    person_id: string
    fake_name: string | null
    degree: number
}

// ── Anomaly ───────────────────────────────────────────────────────────────────
export type EntityType = 'person' | 'event'
export type AnomalyAlgorithm = 'isolation_forest' | 'z_score' | 'rule_based'

export interface AnomalyRecord {
    id: string
    entity_id: string
    entity_type: EntityType
    anomaly_type: string
    score: number
    description: string
    algorithm: AnomalyAlgorithm
    detected_at: string
    created_at: string
}

export interface DetectionResult {
    flagged: number
    skipped_duplicates: number   // AUDIT FIX: was missing
    duration_ms: number
}

// ── User ──────────────────────────────────────────────────────────────────────
export interface UserResponse {
    id: string
    username: string
    is_active: boolean
}

// ── API Pagination ────────────────────────────────────────────────────────────
export interface ApiError {
    detail: string
}
