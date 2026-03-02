/**
 * Spectra — Graph Page
 * Search for a person → fetch N-hop neighbourhood → render with Cytoscape.
 */
import { useState, useCallback } from 'react'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import CytoscapeGraph from '../components/graph/CytoscapeGraph'
import { listPersons } from '../api/persons'
import { getNeighbourhood } from '../api/graph'
import type { NeighbourhoodResponse, Person } from '../types'

export default function GraphPage() {
    const [query, setQuery] = useState('')
    const [searchResults, setSearchResults] = useState<Person[]>([])
    const [searching, setSearching] = useState(false)
    const [searchErr, setSearchErr] = useState<string | null>(null)

    const [selected, setSelected] = useState<Person | null>(null)
    const [hops, setHops] = useState(2)
    const [graph, setGraph] = useState<NeighbourhoodResponse | null>(null)
    const [graphLoading, setGraphLoading] = useState(false)
    const [graphErr, setGraphErr] = useState<string | null>(null)

    const handleSearch = useCallback(async () => {
        if (!query.trim()) return
        setSearching(true)
        setSearchErr(null)
        try {
            const results = await listPersons({ search: query.trim(), limit: 10 })
            setSearchResults(results)
        } catch (e: unknown) {
            setSearchErr((e as { message?: string }).message ?? 'Search failed')
        } finally {
            setSearching(false)
        }
    }, [query])

    const handleSelect = useCallback(async (person: Person) => {
        setSelected(person)
        setSearchResults([])
        setGraph(null)
        setGraphErr(null)
        setGraphLoading(true)
        try {
            const data = await getNeighbourhood(person.id, hops)
            setGraph(data)
        } catch (e: unknown) {
            setGraphErr((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Graph fetch failed')
        } finally {
            setGraphLoading(false)
        }
    }, [hops])

    const handleHopsChange = useCallback(async (newHops: number) => {
        setHops(newHops)
        if (!selected) return
        setGraphLoading(true)
        setGraphErr(null)
        try {
            const data = await getNeighbourhood(selected.id, newHops)
            setGraph(data)
        } catch {
            setGraphErr('Failed to update graph')
        } finally {
            setGraphLoading(false)
        }
    }, [selected])

    return (
        <Layout>
            <div className="mb-6">
                <h1 className="text-2xl font-black text-slate-100">Graph Explorer</h1>
                <p className="text-slate-500 text-sm mt-1">Search a synthetic person and explore their network.</p>
            </div>

            {/* Search bar */}
            <div className="flex gap-3 mb-4">
                <input
                    id="graph-search-input"
                    type="text"
                    placeholder="Search person by name…"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className="flex-1 rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-slate-100 text-sm
                     focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors"
                />
                <button
                    id="graph-search-btn"
                    onClick={handleSearch}
                    disabled={searching}
                    className="px-5 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium
                     disabled:opacity-50 transition-colors"
                >
                    {searching ? '…' : 'Search'}
                </button>
            </div>

            <ErrorMessage message={searchErr} />

            {/* Search results dropdown */}
            {searchResults.length > 0 && (
                <div className="rounded-xl border border-slate-700 bg-slate-900 divide-y divide-slate-800 mb-6 overflow-hidden">
                    {searchResults.map((p) => (
                        <button
                            key={p.id}
                            onClick={() => handleSelect(p)}
                            className="w-full flex items-center gap-4 px-5 py-3 text-left hover:bg-slate-800 transition-colors"
                        >
                            <span className="text-xl">👤</span>
                            <div>
                                <p className="text-slate-200 text-sm font-medium">{p.fake_name}</p>
                                <p className="text-slate-500 text-xs">{p.occupation ?? 'Unknown occupation'}</p>
                            </div>
                        </button>
                    ))}
                </div>
            )}

            {/* Selected person + hop control */}
            {selected && (
                <div className="flex items-center gap-6 mb-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                    <div>
                        <p className="text-slate-200 font-semibold">{selected.fake_name}</p>
                        <p className="text-slate-500 text-xs">{selected.id}</p>
                    </div>
                    <div className="ml-auto flex items-center gap-3">
                        <label className="text-xs text-slate-400">Hops:</label>
                        {[1, 2, 3].map((h) => (
                            <button
                                key={h}
                                onClick={() => handleHopsChange(h)}
                                className={`w-8 h-8 rounded-lg text-sm font-bold transition-colors
                  ${hops === h
                                        ? 'bg-violet-600 text-white'
                                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                                    }`}
                            >
                                {h}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Graph */}
            {graphLoading && <LoadingSpinner />}
            <ErrorMessage message={graphErr} />

            {graph && !graphLoading && (
                <>
                    <div className="flex gap-4 mb-3 text-xs text-slate-500">
                        <span>🟣 Person node</span>
                        <span>🔷 Location node</span>
                        <span>{graph.nodes.length} nodes · {graph.edges.length} edges</span>
                    </div>
                    <CytoscapeGraph data={graph} height={500} />
                </>
            )}

            {!selected && !graphLoading && (
                <div className="flex flex-col items-center justify-center py-24 text-slate-600">
                    <span className="text-5xl mb-4">🕸️</span>
                    <p className="text-sm">Search for a person to explore their graph</p>
                </div>
            )}
        </Layout>
    )
}
