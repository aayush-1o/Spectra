import { client, TOKEN_STORAGE_KEY } from './client'
import type { LoginRequest, RegisterRequest, TokenResponse } from '../types'

export async function register(data: RegisterRequest): Promise<void> {
    await client.post('/api/v1/auth/register', data)
}

export async function login(data: LoginRequest): Promise<string> {
    const res = await client.post<TokenResponse>('/api/v1/auth/login', data)
    const token = res.data.access_token
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    return token
}

export function logout(): void {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
}
