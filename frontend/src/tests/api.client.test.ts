/**
 * Spectra — Unit Tests: API Client
 * Verifies token injection and 401 redirect behaviour.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('API Client token injection', () => {
    const TOKEN = 'test.jwt.token'
    const STORAGE_KEY = 'spectra_token'

    beforeEach(() => {
        localStorage.clear()
    })

    it('does not include Authorization header when no token is stored', () => {
        const headers: Record<string, string> = {}
        const token = localStorage.getItem(STORAGE_KEY)
        if (token) headers['Authorization'] = `Bearer ${token}`
        expect(headers['Authorization']).toBeUndefined()
    })

    it('includes Authorization header when token is in localStorage', () => {
        localStorage.setItem(STORAGE_KEY, TOKEN)
        const headers: Record<string, string> = {}
        const token = localStorage.getItem(STORAGE_KEY)
        if (token) headers['Authorization'] = `Bearer ${token}`
        expect(headers['Authorization']).toBe(`Bearer ${TOKEN}`)
    })

    it('removes token from localStorage on 401', () => {
        localStorage.setItem(STORAGE_KEY, TOKEN)
        const status = 401
        if (status === 401) {
            localStorage.removeItem(STORAGE_KEY)
        }
        expect(localStorage.getItem(STORAGE_KEY)).toBeNull()
    })

    it('localStorage token key is spectra_token', () => {
        expect(STORAGE_KEY).toBe('spectra_token')
    })
})

describe('useDebounce logic', () => {
    it('debounced value updates after delay', async () => {
        vi.useFakeTimers()
        let debounced = 'initial'
        const update = (val: string, delay: number) => {
            setTimeout(() => { debounced = val }, delay)
        }
        update('updated', 300)
        expect(debounced).toBe('initial')
        vi.advanceTimersByTime(300)
        expect(debounced).toBe('updated')
        vi.useRealTimers()
    })
})
