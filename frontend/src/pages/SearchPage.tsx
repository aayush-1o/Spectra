/**
 * Spectra — Search Page (Phase 8)
 * Combines classic name search with Claude-powered NL Search.
 */
import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import NLSearchBar from '../components/shared/NLSearchBar'
import RiskBadge from '../components/shared/RiskBadge'
import { listPersons } from '../api/persons'
import type { Person } from '../types'

function useDebounce<T>(value: T, delay: number) {
    const [debounced, setDebounced] = useState(value)
    useEffect(() => {
        const id = setTimeout(() => setDebounced(value), delay)
        return () => clearTimeout(id)
    }, [value, delay])
    return debounced
}

export default function SearchPage() {
    const navigate = useNavigate()
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<Person[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [activeTab, setActiveTab] = useState<'name' | 'ai'>('name')

    const debouncedQuery = useDebounce(query, 300)

    const search = useCallback(async (q: string) => {
        if (!q.trim()) { setResults([]); return }
        setLoading(true)
        setError(null)
        try {
            const data = await listPersons({ search: q.trim(), limit: 20 })
            setResults(data)
        } catch (e: unknown) {
            setError((e as { message?: string }).message ?? 'Search failed')
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => { search(debouncedQuery) }, [debouncedQuery, search])

    return (
        <Layout>
            <div className="mb-6">
                <h1 className="text-2xl font-black text-slate-100">Person Search</h1>
                <p className="text-slate-500 text-sm mt-1">Find synthetic persons by name or natural language query.</p>
            </div>

            {/* Tab toggle */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setActiveTab('name')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'name'
                            ? 'bg-violet-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                >
                    🔍 Name Search
                </button>
                <button
                    onClick={() => setActiveTab('ai')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'ai'
                            ? 'bg-violet-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                >
                    ✨ AI Search
                </button>
            </div>

            {activeTab === 'ai' ? (
                <NLSearchBar />
            ) : (
                <>
                    {/* Classic name search bar */}
                    <div className="relative mb-6">
                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
                        <input
                            id="global-search-input"
                            type="text"
                            placeholder="Type a name to search…"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="w-full rounded-xl bg-slate-800 border border-slate-700 pl-11 pr-4 py-3 text-slate-100
                             text-sm focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors"
                            autoFocus
                        />
                        {loading && (
                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-violet-400 text-xs animate-pulse">
                                searching…
                            </span>
                        )}
                    </div>

                    <ErrorMessage message={error} />

                    {/* Results grid */}
                    {results.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {results.map((p) => (
                                <button
                                    key={p.id}
                                    onClick={() => navigate(`/person/${p.id}`)}
                                    className="flex items-center gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/40
                                     hover:border-violet-500/40 hover:bg-slate-800/60 text-left transition-all group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-300 text-lg flex-shrink-0">
                                        👤
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <p className="text-slate-200 font-semibold text-sm group-hover:text-violet-300 transition-colors truncate">
                                            {p.fake_name}
                                        </p>
                                        <p className="text-slate-500 text-xs truncate">{p.occupation ?? 'Unknown'}</p>
                                    </div>
                                    <RiskBadge score={p.risk_score} showLabel={false} size="sm" />
                                </button>
                            ))}
                        </div>
                    )}

                    {query && !loading && results.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-slate-600">
                            <span className="text-4xl mb-3">🤷</span>
                            <p className="text-sm">No persons found matching "{query}"</p>
                        </div>
                    )}

                    {!query && (
                        <div className="flex flex-col items-center justify-center py-24 text-slate-700">
                            <span className="text-5xl mb-4">🔍</span>
                            <p className="text-sm">Start typing to search synthetic persons</p>
                        </div>
                    )}

                    {loading && !results.length && <LoadingSpinner />}
                </>
            )}
        </Layout>
    )
}
