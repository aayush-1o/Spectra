import { client } from './client'
import type { Location } from '../types'

export async function listLocations(params?: {
    limit?: number
    offset?: number
}): Promise<Location[]> {
    const res = await client.get<Location[]>('/api/v1/locations', { params })
    return res.data
}
