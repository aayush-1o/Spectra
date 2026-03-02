/**
 * Spectra — Auth Context
 * Stores token + provides login/logout actions.
 * Reads from localStorage on initial mount so the session survives page refresh.
 */

import { createContext, useState, useEffect, type ReactNode } from 'react'
import { TOKEN_STORAGE_KEY } from '../api/client'
import * as authApi from '../api/auth'

interface AuthContextValue {
    token: string | null
    isAuthenticated: boolean
    login: (username: string, password: string) => Promise<void>
    logout: () => void
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue>({
    token: null,
    isAuthenticated: false,
    login: async () => { },
    logout: () => { },
})

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setToken] = useState<string | null>(() =>
        localStorage.getItem(TOKEN_STORAGE_KEY)
    )

    // Keep state in sync if another tab logs out
    useEffect(() => {
        const handler = (e: StorageEvent) => {
            if (e.key === TOKEN_STORAGE_KEY) {
                setToken(e.newValue)
            }
        }
        window.addEventListener('storage', handler)
        return () => window.removeEventListener('storage', handler)
    }, [])

    const login = async (username: string, password: string) => {
        const newToken = await authApi.login({ username, password })
        setToken(newToken)
    }

    const logout = () => {
        authApi.logout()
        setToken(null)
    }

    return (
        <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, logout }
        }>
            {children}
        </AuthContext.Provider>
    )
}
