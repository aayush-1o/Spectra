/**
 * Spectra — NL Search Bar
 * Natural language search powered by Claude.
 * Sends query to POST /api/v1/search/nl and shows matching persons.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { nlSearch } from '../../api/persons'
import type { Person } from '../../types'
import RiskBadge from './RiskBadge'

interface NLSearchBarProps {
    onResults?: (persons: Person[]) => void
}

export default function NLSearchBar({ onResults }: NLSearchBarProps) {
    const navigate = useNavigate()
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [results, setResults] = useState<Person[] | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [resultMeta, setResultMeta] = useState<{ total: number; query: string } | null>(null)

    const handleSearch = async () => {
        if (!query.trim()) return
        setLoading(true)
        setError(null)
        setResults(null)
        setResultMeta(null)
        try {
            const data = await nlSearch(query.trim())
            setResults(data.persons)
            setResultMeta({ total: data.total, query: data.query })
            onResults?.(data.persons)
        } catch (e: unknown) {
            setError((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
                ?? 'Search failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="mb-6">
            {/* Search input */}
            <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-violet-400 text-lg pointer-events-none">
                    ✨
                </span>
                <input
                    id="nl-search-input"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Ask anything… e.g. find people who transferred over $5k at night"
                    className="w-full rounded-xl bg-slate-800/80 border border-violet-500/30 pl-12 pr-32 py-4
                        text-slate-100 text-sm focus:outline-none focus:border-violet-500 focus:ring-1
                        focus:ring-violet-500 transition-all placeholder:text-slate-500"
                    autoComplete="off"
                />
                <button
                    id="nl-search-btn"
                    onClick={handleSearch}
                    disabled={loading || !query.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 rounded-lg
                        bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm
                        font-medium transition-all flex items-center gap-2"
                >
                    {loading ? (
                        <span className="animate-pulse text-xs">Thinking…</span>
                    ) : (
                        'Ask AI'
                    )}
                </button>
            </div>

            {/* Loading state */}
            {loading && (
                <div className="mt-3 flex items-center gap-2 text-violet-400 text-sm animate-pulse">
                    <span>🧠</span>
                    <span>Claude is parsing your query…</span>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="mt-3 text-red-400 text-sm bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    {error}
                </div>
            )}

            {/* Results summary */}
            {resultMeta && !loading && (
                <div className="mt-3 text-sm text-slate-400 flex items-center gap-2">
                    <span className="text-emerald-400">✓</span>
                    Found <span className="text-slate-200 font-semibold">{resultMeta.total}</span> persons matching your query
                </div>
            )}

            {/* Results list */}
            {results && results.length > 0 && !loading && (
                <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {results.map((p) => (
                        <button
                            key={p.id}
                            onClick={() => navigate(`/person/${p.id}`)}
                            className="flex items-center gap-3 p-4 rounded-xl border border-slate-800
                                bg-slate-900/40 hover:border-violet-500/40 hover:bg-slate-800/60
                                text-left transition-all group"
                        >
                            <div className="w-9 h-9 rounded-full bg-violet-600/20 border border-violet-500/30
                                flex items-center justify-center text-violet-300 flex-shrink-0">
                                👤
                            </div>
                            <div className="min-w-0 flex-1">
                                <p className="text-slate-200 font-semibold text-sm group-hover:text-violet-300
                                    transition-colors truncate">
                                    {p.fake_name}
                                </p>
                                <p className="text-slate-500 text-xs truncate">{p.occupation ?? 'Unknown'}</p>
                            </div>
                            <RiskBadge score={p.risk_score} showLabel={false} size="sm" />
                        </button>
                    ))}
                </div>
            )}

            {results && results.length === 0 && !loading && (
                <div className="mt-4 text-center text-slate-500 py-8 border border-dashed border-slate-700 rounded-xl">
                    No persons matched your query
                </div>
            )}
        </div>
    )
}
