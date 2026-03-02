import { client } from './client'
import type { Person } from '../types'

export async function listPersons(params?: {
    limit?: number
    offset?: number
    search?: string
}): Promise<Person[]> {
    const res = await client.get<Person[]>('/api/v1/persons', { params })
    return res.data
}
