/**
 * Spectra — Cytoscape Graph Wrapper
 * Phase 8: Nodes colored by risk_score; community coloring via toggle.
 */
import { useEffect, useRef, useState } from 'react'
import cytoscape, { type Core } from 'cytoscape'
import type { NeighbourhoodResponse } from '../../types'
import { client } from '../../api/client'

interface CytoscapeGraphProps {
    data: NeighbourhoodResponse
    height?: number
}

// ── Color helpers ─────────────────────────────────────────────────────────────

/** Returns a color for a given risk score (0-100). Low = green, High = red. */
function riskColor(score: number | undefined): string {
    if (score === undefined || score === null) return '#7c3aed'
    if (score <= 25) return '#22c55e'
    if (score <= 50) return '#f59e0b'
    if (score <= 75) return '#f97316'
    return '#ef4444'
}

/** 12-color palette for community IDs */
const COMMUNITY_PALETTE = [
    '#7c3aed', '#0891b2', '#059669', '#d97706',
    '#dc2626', '#9333ea', '#0369a1', '#047857',
    '#b45309', '#9f1239', '#6d28d9', '#0e7490',
]

function communityColor(communityId: number): string {
    return COMMUNITY_PALETTE[communityId % COMMUNITY_PALETTE.length]
}

export default function CytoscapeGraph({ data, height = 500 }: CytoscapeGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const cyRef = useRef<Core | null>(null)
    const [colorMode, setColorMode] = useState<'risk' | 'community'>('risk')
    const [communities, setCommunities] = useState<Record<string, number>>({})

    // Fetch communities on mount
    useEffect(() => {
        client.get<{ communities: Record<string, number> }>('/api/v1/graph/communities')
            .then((res) => setCommunities(res.data.communities))
            .catch(() => { /* degrade gracefully if unavailable */ })
    }, [])

    useEffect(() => {
        if (!containerRef.current) return

        const elements = [
            ...data.nodes.map((n) => {
                const riskScore = n.properties.risk_score as number | undefined
                const communityId = communities[n.id]
                const bgColor = colorMode === 'community' && communityId !== undefined
                    ? communityColor(communityId)
                    : n.label === 'Person'
                        ? riskColor(riskScore)
                        : '#0891b2'

                return {
                    data: {
                        id: n.id,
                        label: n.properties.fake_name ?? n.properties.fake_address ?? n.id.slice(0, 8),
                        type: n.label,
                        risk_score: riskScore,
                        community: communityId,
                        bgColor,
                    },
                }
            }),
            ...data.edges.map((e, i) => ({
                data: {
                    id: `e${i}`,
                    source: e.source,
                    target: e.target,
                    label: e.type,
                },
            })),
        ]

        const cy = cytoscape({
            container: containerRef.current,
            elements,
            layout: {
                name: 'cose',
                animate: true,
                animationDuration: 500,
                nodeRepulsion: () => 8000,
            } as cytoscape.LayoutOptions,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(bgColor)',
                        'border-color': '#1e293b',
                        'border-width': 2,
                        label: 'data(label)',
                        color: '#e2e8f0',
                        'font-size': 10,
                        'text-valign': 'bottom',
                        'text-margin-y': 4,
                        width: 32,
                        height: 32,
                    },
                },
                {
                    selector: 'node[type="Location"]',
                    style: {
                        shape: 'diamond',
                        'background-color': '#0891b2',
                        'border-color': '#67e8f9',
                        width: 24,
                        height: 24,
                        'font-size': 9,
                    },
                },
                {
                    selector: 'edge',
                    style: {
                        'line-color': '#475569',
                        'target-arrow-color': '#475569',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        label: 'data(label)',
                        'font-size': 8,
                        color: '#64748b',
                        width: 1.5,
                    },
                },
                {
                    selector: 'node:selected',
                    style: { 'background-color': '#f59e0b', 'border-color': '#fbbf24' },
                },
            ],
        })

        cyRef.current = cy
        return () => { cy.destroy() }
    }, [data, colorMode, communities])

    return (
        <div>
            {/* Color mode toggle */}
            <div className="flex items-center gap-2 mb-3">
                <span className="text-slate-500 text-xs">Color by:</span>
                <button
                    onClick={() => setColorMode('risk')}
                    className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${colorMode === 'risk'
                            ? 'bg-violet-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                >
                    ⚠️ Risk Score
                </button>
                <button
                    onClick={() => setColorMode('community')}
                    className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${colorMode === 'community'
                            ? 'bg-violet-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                >
                    🫧 Community
                </button>

                {/* Risk legend */}
                {colorMode === 'risk' && (
                    <div className="ml-4 flex items-center gap-3 text-xs">
                        {[['#22c55e', 'Low'], ['#f59e0b', 'Med'], ['#f97316', 'High'], ['#ef4444', 'Critical']].map(([color, label]) => (
                            <span key={label} className="flex items-center gap-1">
                                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
                                <span className="text-slate-500">{label}</span>
                            </span>
                        ))}
                    </div>
                )}
                {colorMode === 'community' && (
                    <span className="ml-4 text-xs text-slate-500">
                        {Object.keys(communities).length > 0
                            ? `${new Set(Object.values(communities)).size} communities detected`
                            : 'Loading communities…'}
                    </span>
                )}
            </div>

            <div
                ref={containerRef}
                style={{ width: '100%', height, background: '#0d1117', borderRadius: 12, border: '1px solid #1e293b' }}
            />
        </div>
    )
}
