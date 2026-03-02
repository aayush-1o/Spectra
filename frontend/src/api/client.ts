/**
 * Spectra — Axios Client
 * Single shared instance with JWT injection + 401 auto-redirect.
 */

import axios from 'axios'

const TOKEN_KEY = 'spectra_token'

export const client = axios.create({
    baseURL: '/',
    headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — inject Bearer token ─────────────────────────────────
client.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// ── Response interceptor — 401 → clear token + redirect to login ─────────────
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem(TOKEN_KEY)
            // Avoid redirect loop if already on login/register
            if (!window.location.pathname.startsWith('/login') &&
                !window.location.pathname.startsWith('/register')) {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export const TOKEN_STORAGE_KEY = TOKEN_KEY
