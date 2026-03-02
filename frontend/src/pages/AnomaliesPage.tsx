/**
 * Spectra — Anomalies Page
 * Sortable table of anomaly records + run-detection trigger.
 */
import { useState, useCallback } from 'react'
import Layout from '../components/layout/Layout'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'
import Pagination from '../components/ui/Pagination'
import { useApi } from '../hooks/useApi'
import { listAnomalies, runDetection } from '../api/anomalies'
import type { AnomalyAlgorithm } from '../types'

const LIMIT = 20
const ALGO_COLOR: Record<AnomalyAlgorithm, 'rose' | 'amber' | 'slate'> = {
    isolation_forest: 'rose',
    z_score: 'amber',
    rule_based: 'slate',
}

function fmt(dt: string) {
    return new Date(dt).toLocaleString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
}

export default function AnomaliesPage() {
    const [offset, setOffset] = useState(0)
    const [running, setRunning] = useState(false)
    const [runResult, setRunResult] = useState<string | null>(null)
    const [runErr, setRunErr] = useState<string | null>(null)
    const [sortDesc, setSortDesc] = useState(true)

    const { data, loading, error, refetch } = useApi(
        () => listAnomalies({ limit: LIMIT, offset }),
        [offset]
    )

    const handleRunDetection = useCallback(async () => {
        setRunning(true)
        setRunResult(null)
        setRunErr(null)
        try {
            const result = await runDetection()
            setRunResult(`Detection complete — ${result.flagged} anomalies flagged in ${result.duration_ms.toFixed(0)}ms`)
            refetch()
        } catch (e: unknown) {
            setRunErr((e as { message?: string }).message ?? 'Detection failed')
        } finally {
            setRunning(false)
        }
    }, [refetch])

    const sorted = [...(data ?? [])].sort((a, b) =>
        sortDesc ? b.score - a.score : a.score - b.score
    )

    return (
        <Layout>
            <div className="flex items-start justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-black text-slate-100">Anomaly Detection</h1>
                    <p className="text-slate-500 text-sm mt-1">IsolationForest + z-score outlier detection on synthetic events.</p>
                </div>
                <button
                    id="run-detection-btn"
                    onClick={handleRunDetection}
                    disabled={running}
                    className="px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold
                     disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                    {running ? (
                        <><span className="animate-spin">⏳</span> Running…</>
                    ) : (
                        <>🚀 Run Detection</>
                    )}
                </button>
            </div>

            {runResult && (
                <div className="mb-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 px-4 py-3 text-emerald-300 text-sm">
                    ✅ {runResult}
                </div>
            )}
            <ErrorMessage message={error ?? runErr} />

            {loading && <LoadingSpinner />}

            {sorted.length > 0 && !loading && (
                <>
                    <div className="rounded-xl border border-slate-800 overflow-hidden">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-900/60 border-b border-slate-800">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Entity ID</th>
                                    <th
                                        className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer select-none hover:text-slate-200"
                                        onClick={() => setSortDesc((d) => !d)}
                                    >
                                        Score {sortDesc ? '▼' : '▲'}
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Algorithm</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider hidden md:table-cell">Description</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell">Detected</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {sorted.map((rec) => (
                                    <tr key={rec.id} className="hover:bg-slate-800/40 transition-colors">
                                        <td className="px-4 py-3 font-mono text-xs text-slate-400">{rec.entity_id.slice(0, 12)}…</td>
                                        <td className="px-4 py-3">
                                            <span className={`font-bold text-sm ${rec.score >= 0.8 ? 'text-rose-400' : rec.score >= 0.5 ? 'text-amber-400' : 'text-slate-400'}`}>
                                                {(rec.score * 100).toFixed(0)}%
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <Badge label={rec.algorithm.replace('_', ' ')} color={ALGO_COLOR[rec.algorithm]} />
                                        </td>
                                        <td className="px-4 py-3 text-slate-400 max-w-xs truncate hidden md:table-cell">{rec.description}</td>
                                        <td className="px-4 py-3 text-slate-600 text-xs whitespace-nowrap hidden lg:table-cell">{fmt(rec.detected_at)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <Pagination
                        offset={offset}
                        limit={LIMIT}
                        hasMore={(data?.length ?? 0) === LIMIT}
                        onPrev={() => setOffset((o) => Math.max(0, o - LIMIT))}
                        onNext={() => setOffset((o) => o + LIMIT)}
                    />
                </>
            )}

            {!loading && sorted.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 text-slate-600">
                    <span className="text-5xl mb-4">🔍</span>
                    <p className="text-sm">No anomalies yet. Click "Run Detection" to analyse events.</p>
                </div>
            )}
        </Layout>
    )
}
