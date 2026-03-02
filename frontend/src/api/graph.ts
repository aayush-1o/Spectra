import { client } from './client'
import type { NeighbourhoodResponse, CentralityEntry } from '../types'

export async function getNeighbourhood(
    personId: string,
    hops: number = 2
): Promise<NeighbourhoodResponse> {
    const res = await client.get<NeighbourhoodResponse>(
        `/api/v1/graph/neighbourhood/${personId}`,
        { params: { hops } }
    )
    return res.data
}

export async function getCentrality(topN: number = 20): Promise<CentralityEntry[]> {
    const res = await client.get<CentralityEntry[]>('/api/v1/graph/centrality', {
        params: { top_n: topN },
    })
    return res.data
}

export async function getShortestPath(fromId: string, toId: string): Promise<string[]> {
    const res = await client.get<{ path: string[] }>('/api/v1/graph/shortest-path', {
        params: { from_id: fromId, to_id: toId },
    })
    return res.data.path
}
