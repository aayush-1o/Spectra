/**
 * Spectra — Sidebar Navigation
 */
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const NAV = [
    { to: '/', icon: '📊', label: 'Dashboard' },
    { to: '/map', icon: '🗺️', label: 'Map' },
    { to: '/graph', icon: '🕸️', label: 'Graph' },
    { to: '/anomalies', icon: '🚨', label: 'Anomalies' },
    { to: '/search', icon: '🔍', label: 'Search' },
    { to: '/about', icon: '🛡️', label: 'Ethics' },
]

export default function Sidebar() {
    const { logout } = useAuth()

    return (
        <aside className="flex flex-col w-56 shrink-0 bg-[#0d1117] border-r border-slate-800 h-full">
            {/* Logo */}
            <div className="flex items-center gap-2 px-5 py-5 border-b border-slate-800">
                <span className="text-2xl">🔭</span>
                <span className="text-lg font-black bg-gradient-to-r from-cyan-400 to-violet-500 bg-clip-text text-transparent tracking-tight">
                    Spectra
                </span>
            </div>

            {/* Nav links */}
            <nav className="flex-1 py-4 space-y-1 px-2">
                {NAV.map(({ to, icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
              ${isActive
                                ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30'
                                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                            }`
                        }
                    >
                        <span className="text-base">{icon}</span>
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* Logout */}
            <div className="px-2 pb-4 border-t border-slate-800 pt-4">
                <button
                    onClick={logout}
                    className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-all"
                >
                    <span>↩</span>
                    Logout
                </button>
            </div>
        </aside>
    )
}
