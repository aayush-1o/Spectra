/**
 * Spectra — Dashboard Page
 * KPI cards + recent events feed.
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
    login: 'rose',
}

function fmt(dt: string) {
    return new Date(dt).toLocaleString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
}

export default function DashboardPage() {
    const persons = useApi(() => listPersons({ limit: 1 }))
    const events = useApi(() => listEvents({ limit: 10 }))
    const anomalies = useApi(() => listAnomalies({ limit: 1 }))

    // Use the full list for totals (limit=1 just to get the array length, count from a wider call)
    const personsTotal = useApi(() => listPersons({ limit: 100 }))
    const eventsTotal = useApi(() => listEvents({ limit: 100 }))
    const anomTotal = useApi(() => listAnomalies({ limit: 100 }))

    void persons; void anomalies; // suppress unused

    return (
        <Layout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-black text-slate-100">Dashboard</h1>
                <p className="text-slate-500 text-sm mt-1">Synthetic data overview — all computer-generated.</p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
                <KpiCard
                    icon="👤"
                    label="Total Persons"
                    value={personsTotal.data?.length ?? null}
                    loading={personsTotal.loading}
                    color="violet"
                />
                <KpiCard
                    icon="⚡"
                    label="Total Events"
                    value={eventsTotal.data?.length ?? null}
                    loading={eventsTotal.loading}
                    color="cyan"
                />
                <KpiCard
                    icon="🚨"
                    label="Anomalies"
                    value={anomTotal.data?.length ?? null}
                    loading={anomTotal.loading}
                    color="rose"
                />
            </div>

            {/* Recent Events */}
            <div>
                <h2 className="text-slate-300 font-semibold text-base mb-4">Recent Events</h2>

                {events.loading && <LoadingSpinner />}
                <ErrorMessage message={events.error} />

                {events.data && !events.loading && (
                    <div className="rounded-xl border border-slate-800 bg-slate-900/40 divide-y divide-slate-800 overflow-hidden">
                        {events.data.length === 0 && (
                            <p className="px-5 py-8 text-center text-slate-500 text-sm">No events found. Run the data generator first.</p>
                        )}
                        {events.data.map((ev) => (
                            <div key={ev.id} className="flex items-center gap-4 px-5 py-3">
                                <Badge label={ev.event_type} color={EVENT_BADGE_COLOR[ev.event_type] ?? 'slate'} />
                                <span className="text-slate-400 text-sm font-mono flex-1 truncate">
                                    {ev.actor_id.slice(0, 8)}… → {ev.target_id.slice(0, 8)}…
                                </span>
                                <span className="text-slate-600 text-xs whitespace-nowrap">{fmt(ev.occurred_at)}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Ethics footer */}
            <footer className="mt-16 text-center text-slate-700 text-xs pb-4">
                ⚠️ All data is 100% synthetic. No real people are tracked.
            </footer>
        </Layout>
    )
}
