/**
 * Spectra — Login Page
 */
import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import EthicsBanner from '../components/layout/EthicsBanner'

export default function LoginPage() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)
        try {
            await login(username, password)
            navigate('/')
        } catch (err: unknown) {
            const msg = (err as { response?: { data?: { detail?: string } } })
                ?.response?.data?.detail ?? 'Login failed. Check your credentials.'
            setError(msg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col" style={{ background: '#0a0f1e' }}>
            <EthicsBanner />
            <div className="flex flex-1 items-center justify-center px-4" style={{ marginTop: '44px' }}>
                <div className="w-full max-w-sm">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <div className="text-5xl mb-3">🔭</div>
                        <h1 className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-violet-500 bg-clip-text text-transparent">
                            Spectra
                        </h1>
                        <p className="text-slate-500 text-sm mt-1">Synthetic Analytics Platform</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4 bg-slate-900/60 border border-slate-800 rounded-2xl p-8">
                        <h2 className="text-slate-200 font-semibold text-lg mb-2">Sign In</h2>

                        {error && (
                            <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-rose-300 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400">Username</label>
                            <input
                                id="login-username"
                                type="text"
                                autoComplete="username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-slate-100 text-sm
                           focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors"
                                placeholder="demo2"
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400">Password</label>
                            <input
                                id="login-password"
                                type="password"
                                autoComplete="current-password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-slate-100 text-sm
                           focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            id="login-submit"
                            type="submit"
                            disabled={loading}
                            className="w-full py-2.5 rounded-lg font-semibold text-sm text-white
                         bg-gradient-to-r from-violet-600 to-cyan-600
                         hover:from-violet-500 hover:to-cyan-500
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {loading ? 'Signing in…' : 'Sign In'}
                        </button>

                        <p className="text-center text-xs text-slate-500 mt-2">
                            No account?{' '}
                            <Link to="/register" className="text-violet-400 hover:text-violet-300 underline">
                                Register
                            </Link>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    )
}
