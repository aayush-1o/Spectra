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

export async function getPersonById(id: string): Promise<Person> {
    const res = await client.get<Person>(`/api/v1/persons/${id}`)
    return res.data
}

export async function getPersonSummary(id: string): Promise<{ summary: string }> {
    const res = await client.get<{ summary: string }>(`/api/v1/persons/${id}/summary`)
    return res.data
}

export async function nlSearch(query: string): Promise<{
    persons: Person[]
    total: number
    query: string
    filters_applied: Record<string, unknown>
}> {
    const res = await client.post('/api/v1/search/nl', { query })
    return res.data
}
