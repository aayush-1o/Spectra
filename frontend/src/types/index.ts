/**
 * Spectra — Shared TypeScript Types
 * All interfaces mirror backend Pydantic schemas exactly.
 *
 * Phase 8: Expanded Person, Location interfaces; added Phase 8 API types.
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
    date_of_birth: string | null
    occupation: string | null
    location_id: string | null
    metadata_: Record<string, unknown>
    // Phase 8 fields
    fake_phone_primary: string | null
    fake_phone_secondary: string | null
    fake_email: string | null
    fake_nationality: string | null
    fake_alias: string | null
    risk_category: string | null
    group_memberships: string[] | null
    fake_id_number: string | null
    risk_score: number | null
    last_seen_lat: number | null
    last_seen_lon: number | null
    last_seen_at: string | null
    created_at: string
}

// ── Location ──────────────────────────────────────────────────────────────────
export type LocationType = 'office' | 'residence' | 'transit_hub' | 'commercial' | 'unknown'

export interface Location {
    id: string
    fake_address: string
    lat: number
    lng: number
    location_type: LocationType
    metadata_: Record<string, unknown>
    // Phase 8 fields
    district: string | null
    threat_level: string | null
    surveillance_coverage: boolean | null
    created_at: string
}

// ── Event ─────────────────────────────────────────────────────────────────────
export type EventType = 'call' | 'message' | 'meeting' | 'transfer'

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
        risk_score?: number
        risk_category?: string
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

// ── Community Detection ───────────────────────────────────────────────────────
export interface CommunitiesResponse {
    communities: Record<string, number>  // person_id -> community_id
    community_count: number
}

// ── Anomaly ───────────────────────────────────────────────────────────────────
export type EntityType = 'person' | 'event'
export type AnomalyAlgorithm =
    | 'isolation_forest'
    | 'z_score'
    | 'rule_based'
    | 'dbscan'
    | 'lof'
    | 'night_owl_rule'

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
    skipped_duplicates: number
    duration_ms: number
    by_algorithm?: Record<string, number>
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

// ── NL Search ─────────────────────────────────────────────────────────────────
export interface NLSearchResult {
    persons: Person[]
    total: number
    query: string
    filters_applied: Record<string, unknown>
}
