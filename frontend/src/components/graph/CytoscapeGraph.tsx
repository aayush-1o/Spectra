/**
 * Spectra — Cytoscape Graph Wrapper
 * Renders nodes + edges from the neighbourhood API.
 */
import { useEffect, useRef } from 'react'
import cytoscape, { type Core } from 'cytoscape'
import type { NeighbourhoodResponse } from '../../types'

interface CytoscapeGraphProps {
    data: NeighbourhoodResponse
    height?: number
}

export default function CytoscapeGraph({ data, height = 500 }: CytoscapeGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const cyRef = useRef<Core | null>(null)

    useEffect(() => {
        if (!containerRef.current) return

        const elements = [
            ...data.nodes.map((n) => ({
                data: {
                    id: n.id,
                    label: n.properties.fake_name ?? n.properties.fake_address ?? n.id.slice(0, 8),
                    type: n.label,
                },
            })),
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
            layout: { name: 'cose', animate: true, animationDuration: 500, nodeRepulsion: () => 8000 } as cytoscape.LayoutOptions,
            style: [
                {
                    selector: 'node[type="Person"]',
                    style: {
                        'background-color': '#7c3aed',
                        'border-color': '#a78bfa',
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
                        'background-color': '#0891b2',
                        'border-color': '#67e8f9',
                        'border-width': 2,
                        label: 'data(label)',
                        color: '#e2e8f0',
                        'font-size': 9,
                        'text-valign': 'bottom',
                        'text-margin-y': 4,
                        shape: 'diamond',
                        width: 24,
                        height: 24,
                    },
                },
                {
                    selector: 'node',
                    style: {
                        'background-color': '#334155',
                        label: 'data(label)',
                        color: '#94a3b8',
                        'font-size': 9,
                        width: 24,
                        height: 24,
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
    }, [data])

    return (
        <div
            ref={containerRef}
            style={{ width: '100%', height, background: '#0d1117', borderRadius: 12, border: '1px solid #1e293b' }}
        />
    )
}
