/**
 * Spectra — Unit Tests: Auth Store
 * Tests the AuthContext login/logout behaviour.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider } from '../store/auth'
import { useAuth } from '../hooks/useAuth'

// Mock the auth API to avoid real HTTP calls
vi.mock('../api/auth', () => ({
    login: vi.fn().mockResolvedValue('mocked-token'),
    logout: vi.fn(),
    register: vi.fn(),
}))

function TestComponent() {
    const { isAuthenticated, login, logout } = useAuth()
    return (
        <div>
            <span data-testid="auth-status">{isAuthenticated ? 'logged-in' : 'logged-out'}</span>
            <button onClick={() => login('user', 'pass')}>Login</button>
            <button onClick={logout}>Logout</button>
        </div>
    )
}

describe('AuthContext', () => {
    beforeEach(() => {
        localStorage.clear()
    })

    it('starts logged-out when localStorage is empty', () => {
        render(<AuthProvider><TestComponent /></AuthProvider>)
        expect(screen.getByTestId('auth-status').textContent).toBe('logged-out')
    })

    it('becomes authenticated after login', async () => {
        const user = userEvent.setup()
        render(<AuthProvider><TestComponent /></AuthProvider>)
        await act(async () => {
            await user.click(screen.getByText('Login'))
        })
        expect(screen.getByTestId('auth-status').textContent).toBe('logged-in')
    })

    it('becomes logged-out after logout', async () => {
        const user = userEvent.setup()
        localStorage.setItem('spectra_token', 'existing-token')
        render(<AuthProvider><TestComponent /></AuthProvider>)
        expect(screen.getByTestId('auth-status').textContent).toBe('logged-in')
        await act(async () => {
            await user.click(screen.getByText('Logout'))
        })
        expect(screen.getByTestId('auth-status').textContent).toBe('logged-out')
    })
})
