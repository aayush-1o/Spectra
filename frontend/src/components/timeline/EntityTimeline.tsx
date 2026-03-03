/**
 * Spectra — Entity Timeline Component
 * Shows all events for a person as a vertical timeline.
 * Color-coded by event type, with anomaly flags.
 *
 * Note: Uses a custom lightweight implementation instead of react-chrono
 * for better compatibility with the existing Vite/React stack.
 */
import { useEffect, useState } from 'react'
import { listEvents } from '../../api/events'
import type { Event, EventType } from '../../types'

interface EntityTimelineProps {
    personId: string
}

const EVENT_COLORS: Record<EventType, { bg: string; text: string; border: string; dot: string }> = {
    call: {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500/30',
        dot: 'bg-blue-500',
    },
    message: {
        bg: 'bg-purple-500/10',
        text: 'text-purple-400',
        border: 'border-purple-500/30',
        dot: 'bg-purple-500',
    },
    transfer: {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
        dot: 'bg-emerald-500',
    },
    meeting: {
        bg: 'bg-orange-500/10',
        text: 'text-orange-400',
        border: 'border-orange-500/30',
        dot: 'bg-orange-500',
    },
}

const EVENT_ICONS: Record<EventType, string> = {
    call: '📞',
    message: '💬',
    transfer: '💸',
    meeting: '🤝',
}

function formatEventDescription(event: Event): string {
    const meta = event.metadata_ || {}
    const time = new Date(event.occurred_at).toLocaleString('en-GB', {
        dateStyle: 'short',
        timeStyle: 'short',
    })

    switch (event.event_type) {
        case 'call': {
            const dur = meta.duration_seconds as number | undefined
            const durStr = dur ? `${Math.floor(dur / 60)}m ${dur % 60}s` : ''
            const channel = meta.channel as string | undefined
            const encrypted = meta.is_encrypted ? '🔒' : ''
            return `${encrypted} Call [${channel ?? 'voice'}] · ${durStr} · ${time}`
        }
        case 'message': {
            const platform = meta.platform as string | undefined
            return `Message via ${platform ?? 'Unknown'} · ${time}`
        }
        case 'transfer': {
            const amount = meta.amount_usd as number | undefined
            const currency = meta.currency as string | undefined
            const amountStr = amount ? `$${amount.toLocaleString()}` : ''
            return `Transfer ${amountStr} ${currency ?? 'USD'} · ${time}`
        }
        case 'meeting': {
            const count = meta.attendee_count as number | undefined
            const covert = meta.is_covert ? '🕵️ COVERT · ' : ''
            return `${covert}Meeting with ${count ?? 2} attendees · ${time}`
        }
        default:
            return time
    }
}

function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    })
}

export default function EntityTimeline({ personId }: EntityTimelineProps) {
    const [events, setEvents] = useState<Event[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        setLoading(true)
        listEvents({ limit: 50, person_id: personId })
            .then(setEvents)
            .catch((e) => setError(e?.message ?? 'Failed to load events'))
            .finally(() => setLoading(false))
    }, [personId])

    if (loading) {
        return (
            <div className="flex items-center gap-2 text-slate-500 text-sm animate-pulse py-4">
                <span>⟳</span> Loading events…
            </div>
        )
    }

    if (error) {
        return <div className="text-red-400 text-sm">{error}</div>
    }

    if (events.length === 0) {
        return (
            <div className="text-slate-600 text-sm text-center py-8 border border-dashed border-slate-700 rounded-lg">
                No events found for this person
            </div>
        )
    }

    return (
        <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-4 top-0 bottom-0 w-px bg-slate-700" />

            <div className="space-y-1">
                {events.map((event, idx) => {
                    const colors = EVENT_COLORS[event.event_type] ?? EVENT_COLORS.call
                    const icon = EVENT_ICONS[event.event_type] ?? '📌'
                    const isAnomaly = (event.anomaly_score ?? 0) > 0
                    const isFirstOfDay = idx === 0
                        || formatDate(events[idx - 1].occurred_at) !== formatDate(event.occurred_at)

                    return (
                        <div key={event.id}>
                            {/* Day separator */}
                            {isFirstOfDay && (
                                <div className="flex items-center gap-3 py-2 pl-12">
                                    <span className="text-slate-500 text-xs font-mono">
                                        {formatDate(event.occurred_at)}
                                    </span>
                                </div>
                            )}

                            {/* Event row */}
                            <div className="flex items-start gap-3 pl-1 py-1.5 group">
                                {/* Dot on timeline */}
                                <div className={`relative z-10 w-7 h-7 rounded-full flex items-center justify-center
                                    flex-shrink-0 mt-0.5 text-sm ${colors.bg} border ${colors.border}`}>
                                    {icon}
                                </div>

                                {/* Content */}
                                <div className={`flex-1 rounded-lg px-3 py-2.5 ${colors.bg} border ${colors.border}
                                    group-hover:border-opacity-60 transition-all`}>
                                    <div className="flex items-start justify-between gap-2">
                                        <div>
                                            <span className={`text-xs font-semibold uppercase tracking-wider ${colors.text}`}>
                                                {event.event_type}
                                            </span>
                                            {isAnomaly && (
                                                <span className="ml-2 text-xs text-red-400 bg-red-500/10 border border-red-500/30
                                                    px-1.5 py-0.5 rounded-full">
                                                    🚨 Anomaly
                                                </span>
                                            )}
                                        </div>
                                        <span className="text-slate-500 text-xs font-mono flex-shrink-0">
                                            {new Date(event.occurred_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                    <p className="text-slate-300 text-sm mt-1">
                                        {formatEventDescription(event)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
