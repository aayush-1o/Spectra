/**
 * Spectra — Anomalies Page (Palantir light theme)
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
    dbscan: 'rose',
    lof: 'amber',
    night_owl_rule: 'slate',
}

function fmt(dt: string) {
    return new Date(dt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

/** Coloured severity bar */
function ScoreBar({ score }: { score: number }) {
    const pct = Math.round(score * 100)
    const color = score >= 0.8 ? '#dc2626' : score >= 0.5 ? '#d97706' : '#16a34a'
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ flex: 1, maxWidth: 80, height: 6, background: '#f1f5f9', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width .3s' }} />
            </div>
            <span style={{ fontSize: 12, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', color, minWidth: 34, textAlign: 'right' }}>
                {pct}%
            </span>
        </div>
    )
}

/** Risk severity label */
function SeverityDot({ score }: { score: number }) {
    if (score >= 0.8) return <span style={{ color: '#dc2626', fontWeight: 700, fontSize: 10, letterSpacing: '.08em' }}>● CRITICAL</span>
    if (score >= 0.5) return <span style={{ color: '#d97706', fontWeight: 700, fontSize: 10, letterSpacing: '.08em' }}>● HIGH</span>
    return <span style={{ color: '#16a34a', fontWeight: 700, fontSize: 10, letterSpacing: '.08em' }}>● NOMINAL</span>
}

export default function AnomaliesPage() {
    const [offset, setOffset] = useState(0)
    const [running, setRunning] = useState(false)
    const [runResult, setRunResult] = useState<string | null>(null)
    const [runErr, setRunErr] = useState<string | null>(null)
    const [sortDesc, setSortDesc] = useState(true)

    const { data, loading, error, refetch } = useApi(
        () => listAnomalies({ limit: LIMIT, offset }), [offset]
    )

    const handleRunDetection = useCallback(async () => {
        setRunning(true); setRunResult(null); setRunErr(null)
        try {
            const result = await runDetection()
            setRunResult(`Detection complete — ${result.flagged} anomalies flagged in ${result.duration_ms.toFixed(0)}ms`)
            refetch()
        } catch (e: unknown) {
            setRunErr((e as { message?: string }).message ?? 'Detection failed')
        } finally { setRunning(false) }
    }, [refetch])

    const sorted = [...(data ?? [])].sort((a, b) => sortDesc ? b.score - a.score : a.score - b.score)

    return (
        <Layout>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 4px' }}>
                        Anomaly Detection
                    </h1>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
                        IsolationForest · z-score · LOF · DBSCAN — synthetic-event outlier detection
                    </p>
                </div>
                <button
                    id="run-detection-btn"
                    onClick={handleRunDetection}
                    disabled={running}
                    style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        padding: '9px 18px', borderRadius: 6,
                        background: running ? '#f1f5f9' : '#4f46e5',
                        color: running ? '#94a3b8' : '#fff',
                        border: `1px solid ${running ? '#e2e8f0' : '#4338ca'}`,
                        fontSize: 13, fontWeight: 600, cursor: running ? 'not-allowed' : 'pointer',
                        boxShadow: running ? 'none' : '0 1px 3px rgba(79,70,229,.3)',
                        transition: 'all .15s',
                    }}
                >
                    {running ? (
                        <>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin">
                                <circle cx="12" cy="12" r="10" strokeOpacity=".3" />
                                <path d="M12 2a10 10 0 0 1 10 10" />
                            </svg>
                            Running…
                        </>
                    ) : (
                        <>
                            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M5 3l8 5-8 5V3z" fill="currentColor" />
                            </svg>
                            Run Detection
                        </>
                    )}
                </button>
            </div>

            {/* Result banner */}
            {runResult && (
                <div style={{ marginBottom: 16, borderRadius: 6, background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#166534', padding: '10px 16px', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#16a34a" strokeWidth="1.5" strokeLinecap="round">
                        <path d="M2 8l4 4L14 4" />
                    </svg>
                    {runResult}
                </div>
            )}
            <ErrorMessage message={error ?? runErr} />
            {loading && <LoadingSpinner />}

            {sorted.length > 0 && !loading && (
                <>
                    {/* Table */}
                    <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 8, boxShadow: 'var(--shadow-sm)', overflow: 'hidden', marginBottom: 16 }}>
                        <table className="spec-table">
                            <thead>
                                <tr>
                                    <th>Severity</th>
                                    <th>Entity ID</th>
                                    <th
                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                        onClick={() => setSortDesc(d => !d)}
                                    >
                                        Risk Score {sortDesc ? '↓' : '↑'}
                                    </th>
                                    <th>Algorithm</th>
                                    <th className="hidden-sm">Description</th>
                                    <th className="hidden-md">Detected</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sorted.map((rec) => (
                                    <tr key={rec.id} style={{
                                        borderLeft: `3px solid ${rec.score >= 0.8 ? '#dc2626' : rec.score >= 0.5 ? '#d97706' : '#16a34a'}`,
                                    }}>
                                        <td><SeverityDot score={rec.score} /></td>
                                        <td>
                                            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, color: 'var(--text-secondary)' }}>
                                                {rec.entity_id.slice(0, 12)}…
                                            </span>
                                        </td>
                                        <td><ScoreBar score={rec.score} /></td>
                                        <td>
                                            <Badge label={rec.algorithm.replace(/_/g, ' ')} color={ALGO_COLOR[rec.algorithm]} />
                                        </td>
                                        <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 12 }}>
                                            {rec.description}
                                        </td>
                                        <td style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                                            {fmt(rec.detected_at)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <Pagination
                        offset={offset}
                        limit={LIMIT}
                        hasMore={(data?.length ?? 0) === LIMIT}
                        onPrev={() => setOffset(o => Math.max(0, o - LIMIT))}
                        onNext={() => setOffset(o => o + LIMIT)}
                    />
                </>
            )}

            {!loading && sorted.length === 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 0', color: 'var(--text-muted)' }}>
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5" style={{ marginBottom: 16 }}>
                        <path d="M12 2L22 20H2L12 2Z" /><line x1="12" y1="9" x2="12" y2="13" /><circle cx="12" cy="16.5" r=".5" fill="#cbd5e1" />
                    </svg>
                    <p style={{ fontSize: 14, fontWeight: 500, margin: 0 }}>No anomalies detected yet</p>
                    <p style={{ fontSize: 12, margin: '6px 0 0' }}>Click "Run Detection" to analyse synthetic events</p>
                </div>
            )}
        </Layout>
    )
}
