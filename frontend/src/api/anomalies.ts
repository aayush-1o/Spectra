import { client } from './client'
import type { AnomalyRecord, DetectionResult } from '../types'

export async function listAnomalies(params?: {
    limit?: number
    offset?: number
}): Promise<AnomalyRecord[]> {
    const res = await client.get<AnomalyRecord[]>('/api/v1/anomalies', { params })
    return res.data
}

export async function runDetection(): Promise<DetectionResult> {
    const res = await client.post<DetectionResult>('/api/v1/anomalies/run-detection')
    return res.data
}
