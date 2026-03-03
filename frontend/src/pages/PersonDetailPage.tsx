/**
 * Spectra — Person Detail Page
 * Route: /person/:id
 * Shows all person fields with AI summary and event timeline.
 */
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import RiskBadge from '../components/shared/RiskBadge'
import AISummaryPanel from '../components/person/AISummaryPanel'
import EntityTimeline from '../components/timeline/EntityTimeline'
import { getPersonById } from '../api/persons'
import type { Person } from '../types'

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
    if (value === null || value === undefined || value === '') return null
    return (
        <div className="flex items-start gap-3 py-2.5 border-b border-slate-800/60 last:border-0">
            <span className="text-slate-500 text-xs font-mono uppercase tracking-wider w-36 flex-shrink-0 pt-0.5">
                {label}
            </span>
            <span className="text-slate-200 text-sm flex-1">{value}</span>
        </div>
    )
}

function calcAge(dob: string | null): string {
    if (!dob) return '—'
    const today = new Date()
    const birth = new Date(dob)
    const age = today.getFullYear() - birth.getFullYear()
    return `${age} years`
}

export default function PersonDetailPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [person, setPerson] = useState<Person | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!id) return
        setLoading(true)
        getPersonById(id)
            .then(setPerson)
            .catch((e) => setError(e?.response?.data?.detail ?? 'Person not found'))
            .finally(() => setLoading(false))
    }, [id])

    if (loading) return <Layout><LoadingSpinner /></Layout>
    if (error || !person) return <Layout><ErrorMessage message={error ?? 'Person not found'} /></Layout>

    return (
        <Layout>
            {/* Header */}
            <div className="mb-6 flex items-start justify-between">
                <div>
                    <button
                        onClick={() => navigate(-1)}
                        className="text-slate-500 hover:text-slate-300 text-sm mb-2 flex items-center gap-1 transition-colors"
                    >
                        ← Back
                    </button>
                    <h1 className="text-3xl font-black text-slate-100">{person.fake_name}</h1>
                    <div className="flex items-center gap-3 mt-2">
                        {person.fake_alias && (
                            <span className="text-xs font-mono text-violet-400 bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded-full">
                                "{person.fake_alias}"
                            </span>
                        )}
                        <span className="text-slate-500 text-sm">{person.occupation ?? 'Unknown occupation'}</span>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <RiskBadge score={person.risk_score} size="lg" />
                    <button
                        id="view-in-graph-btn"
                        onClick={() => navigate(`/graph?personId=${person.id}`)}
                        className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700
                            text-slate-300 text-sm font-medium transition-all flex items-center gap-2"
                    >
                        🕸️ View in Graph
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left column: Profile details */}
                <div className="lg:col-span-1 space-y-4">
                    {/* Identity card */}
                    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
                        <h2 className="text-slate-400 text-xs font-mono uppercase tracking-wider mb-3 flex items-center gap-2">
                            <span>🆔</span> Identity
                        </h2>

                        <DetailRow label="Full Name" value={person.fake_name} />
                        <DetailRow label="ID Number" value={
                            <span className="font-mono text-amber-400">{person.fake_id_number}</span>
                        } />
                        <DetailRow label="Date of Birth" value={person.date_of_birth
                            ? `${person.date_of_birth} (${calcAge(person.date_of_birth)})`
                            : null} />
                        <DetailRow label="Nationality" value={person.fake_nationality} />
                        <DetailRow label="Alias" value={person.fake_alias
                            ? <span className="text-violet-400 font-mono">"{person.fake_alias}"</span>
                            : null} />
                        <DetailRow label="Risk Category" value={person.risk_category?.toUpperCase()} />
                    </div>

                    {/* Contact info */}
                    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
                        <h2 className="text-slate-400 text-xs font-mono uppercase tracking-wider mb-3 flex items-center gap-2">
                            <span>📡</span> Contact
                        </h2>
                        <DetailRow label="Primary Phone" value={person.fake_phone_primary} />
                        <DetailRow label="Secondary Phone" value={person.fake_phone_secondary} />
                        <DetailRow label="Email" value={person.fake_email
                            ? <span className="text-sky-400">{person.fake_email}</span>
                            : null} />
                    </div>

                    {/* Affiliations */}
                    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
                        <h2 className="text-slate-400 text-xs font-mono uppercase tracking-wider mb-3 flex items-center gap-2">
                            <span>🏢</span> Affiliations
                        </h2>
                        {person.group_memberships && person.group_memberships.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {person.group_memberships.map((org) => (
                                    <span key={org} className="text-xs bg-slate-800 border border-slate-700
                                        text-slate-300 px-2 py-1 rounded-md">
                                        {org}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-600 text-sm">No known affiliations</p>
                        )}
                    </div>

                    {/* Similar Persons placeholder (Phase 9) */}
                    <div className="rounded-xl border border-dashed border-slate-700 p-5">
                        <h2 className="text-slate-500 text-xs font-mono uppercase tracking-wider mb-2">
                            🔍 Similar Persons — Phase 9
                        </h2>
                        <p className="text-slate-600 text-xs">
                            Entity similarity matching will be available in Phase 9.
                        </p>
                    </div>
                </div>

                {/* Right column: Timeline + AI Summary */}
                <div className="lg:col-span-2 space-y-6">
                    {/* AI Summary */}
                    <AISummaryPanel personId={person.id} />

                    {/* Event Timeline */}
                    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
                        <h2 className="text-slate-400 text-xs font-mono uppercase tracking-wider mb-4 flex items-center gap-2">
                            <span>📅</span> Event Timeline
                        </h2>
                        {id && <EntityTimeline personId={id} />}
                    </div>
                </div>
            </div>
        </Layout>
    )
}
