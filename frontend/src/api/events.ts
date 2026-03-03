import { client } from './client'
import type { Event } from '../types'

export async function listEvents(params?: {
    limit?: number
    offset?: number
    type?: string
    from_date?: string
    to_date?: string
    person_id?: string  // Phase 8: filter events for a specific person
}): Promise<Event[]> {
    const res = await client.get<Event[]>('/api/v1/events', { params })
    return res.data
}
