/**
 * Spectra — Dashboard Page (Palantir light theme)
 */
import Layout from '../components/layout/Layout'
import KpiCard from '../components/ui/KpiCard'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'
import { useApi } from '../hooks/useApi'
import { listPersons } from '../api/persons'
import { listEvents } from '../api/events'
import { listAnomalies } from '../api/anomalies'
import type { EventType } from '../types'

const EVENT_BADGE_COLOR: Record<EventType, 'cyan' | 'violet' | 'amber' | 'rose' | 'emerald'> = {
    call: 'cyan',
    message: 'violet',
    meeting: 'emerald',
    transfer: 'amber',
}

const EVENT_LABELS: Record<EventType, string> = {
    call: 'CALL', message: 'MSG', meeting: 'MEET', transfer: 'XFER',
}

function fmt(dt: string) {
    return new Date(dt).toLocaleString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
}

/* SVG icons for KPI cards */
const PersonSVG = (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <circle cx="8" cy="5" r="3" /><path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" />
    </svg>
)
const EventSVG = (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
        <path d="M8 1v6l3 3" /><circle cx="8" cy="8" r="7" />
    </svg>
)
const AnomalySVG = (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8 1L15 14H1L8 1Z" /><line x1="8" y1="6" x2="8" y2="9" />
        <circle cx="8" cy="11.5" r=".5" fill="currentColor" />
    </svg>
)

export default function DashboardPage() {
    const personsTotal = useApi(() => listPersons({ limit: 100 }))
    const eventsTotal = useApi(() => listEvents({ limit: 100 }))
    const anomTotal = useApi(() => listAnomalies({ limit: 100 }))
    const events = useApi(() => listEvents({ limit: 12 }))

    return (
        <Layout>
            {/* Page header */}
            <div style={{ marginBottom: 28 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
                    <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                        Intelligence Dashboard
                    </h1>
                    <span style={{
                        fontSize: 10, fontWeight: 600, letterSpacing: '.08em',
                        color: '#16a34a', background: '#dcfce7', border: '1px solid #bbf7d0',
                        borderRadius: 20, padding: '2px 8px',
                    }}>
                        LIVE
                    </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
                    Synthetic-data overview — 100% computer-generated, no real entities.
                </p>
            </div>

            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 28 }}>
                <KpiCard icon={PersonSVG} label="Tracked Entities" value={personsTotal.data?.length ?? null} loading={personsTotal.loading} color="indigo" />
                <KpiCard icon={EventSVG} label="Logged Events" value={eventsTotal.data?.length ?? null} loading={eventsTotal.loading} color="blue" />
                <KpiCard icon={AnomalySVG} label="Active Anomalies" value={anomTotal.data?.length ?? null} loading={anomTotal.loading} color="rose" />
            </div>

            {/* Recent Events */}
            <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 8, boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
                {/* Table header */}
                <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>Recent Events</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>last 12</span>
                </div>

                {events.loading && <LoadingSpinner />}
                <ErrorMessage message={events.error} />

                {events.data && !events.loading && (
                    <table className="spec-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Actor ID</th>
                                <th>Target ID</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {events.data.length === 0 && (
                                <tr>
                                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0' }}>
                                        No events yet — run the data generator.
                                    </td>
                                </tr>
                            )}
                            {events.data.map((ev) => (
                                <tr key={ev.id}>
                                    <td><Badge label={EVENT_LABELS[ev.event_type] ?? ev.event_type} color={EVENT_BADGE_COLOR[ev.event_type] ?? 'slate'} /></td>
                                    <td><span className="mono" style={{ fontSize: 12 }}>{ev.actor_id.slice(0, 8)}…</span></td>
                                    <td><span className="mono" style={{ fontSize: 12 }}>{ev.target_id.slice(0, 8)}…</span></td>
                                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{fmt(ev.occurred_at)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Ethics footer */}
            <div style={{ marginTop: 32, padding: '12px 0', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-muted)', textAlign: 'center' }}>
                ⚠ All data is 100% synthetic. No real people are tracked.
            </div>
        </Layout>
    )
}
