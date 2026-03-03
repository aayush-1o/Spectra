/**
 * Spectra — Sidebar Navigation (Palantir light theme)
 * Dark sidebar with light-mode accent highlights. Professional nav.
 */
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const NAV = [
    { to: '/', label: 'Dashboard', icon: DashIcon },
    { to: '/map', label: 'Locations', icon: MapIcon },
    { to: '/live-map', label: 'Live Tracking', icon: RadarIcon },
    { to: '/graph', label: 'Graph', icon: GraphIcon },
    { to: '/anomalies', label: 'Anomalies', icon: AlertIcon },
    { to: '/search', label: 'Intelligence', icon: SearchIcon },
    { to: '/about', label: 'Ethics', icon: ShieldIcon },
]

export default function Sidebar() {
    const { logout } = useAuth()
    return (
        <aside style={{
            width: 220, flexShrink: 0,
            background: '#0f172a',
            borderRight: '1px solid #1e293b',
            display: 'flex', flexDirection: 'column',
            height: '100%',
            fontFamily: 'Inter, system-ui, sans-serif',
        }}>
            {/* Logo */}
            <div style={{ padding: '20px 16px 16px', borderBottom: '1px solid #1e293b' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                        width: 32, height: 32, borderRadius: 6,
                        background: 'linear-gradient(135deg,#4f46e5,#0284c7)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                    }}>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <circle cx="8" cy="8" r="3" fill="white" fillOpacity=".9" />
                            <circle cx="8" cy="8" r="7" stroke="white" strokeWidth="1.5" strokeOpacity=".4" />
                            <line x1="1" y1="8" x2="15" y2="8" stroke="white" strokeWidth="1" strokeOpacity=".3" />
                            <line x1="8" y1="1" x2="8" y2="15" stroke="white" strokeWidth="1" strokeOpacity=".3" />
                        </svg>
                    </div>
                    <div>
                        <div style={{ fontSize: 14, fontWeight: 800, color: '#f1f5f9', letterSpacing: '.01em' }}>SPECTRA</div>
                        <div style={{ fontSize: 10, color: '#475569', letterSpacing: '.08em', fontWeight: 500 }}>INTEL PLATFORM</div>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto' }}>
                <div style={{ fontSize: 10, color: '#334155', fontWeight: 600, letterSpacing: '.1em', padding: '4px 10px 8px', textTransform: 'uppercase' }}>
                    Navigation
                </div>
                {NAV.map(({ to, label, icon: Icon }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        style={({ isActive }) => ({
                            display: 'flex', alignItems: 'center', gap: 10,
                            padding: '8px 12px', borderRadius: 6, marginBottom: 2,
                            fontSize: 13, fontWeight: isActive ? 600 : 400,
                            color: isActive ? '#a5b4fc' : '#64748b',
                            background: isActive ? 'rgba(99,102,241,.12)' : 'transparent',
                            borderLeft: `2px solid ${isActive ? '#6366f1' : 'transparent'}`,
                            textDecoration: 'none',
                            transition: 'all .12s',
                        })}
                    >
                        {({ isActive }) => (
                            <>
                                <Icon size={15} color={isActive ? '#a5b4fc' : '#475569'} />
                                {label}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* Version + Logout */}
            <div style={{ padding: '12px 8px', borderTop: '1px solid #1e293b' }}>
                <div style={{ padding: '4px 12px 10px', fontSize: 10, color: '#334155', fontFamily: 'JetBrains Mono, monospace' }}>
                    v0.9.0 · synthetic-only
                </div>
                <button
                    onClick={logout}
                    style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        width: '100%', padding: '8px 12px', borderRadius: 6,
                        background: 'transparent', border: 'none',
                        color: '#475569', fontSize: 13, cursor: 'pointer',
                        textAlign: 'left', transition: 'all .12s',
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = '#f87171'; (e.currentTarget as HTMLButtonElement).style.background = 'rgba(239,68,68,.08)' }}
                    onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = '#475569'; (e.currentTarget as HTMLButtonElement).style.background = 'transparent' }}
                >
                    <LogoutIcon size={14} color="currentColor" />
                    Log out
                </button>
            </div>
        </aside>
    )
}

/* ── Inline SVG icons (no external dependency) ───────────────────────── */
function DashIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round">
            <rect x="1" y="1" width="6" height="6" rx="1" />
            <rect x="9" y="1" width="6" height="6" rx="1" />
            <rect x="1" y="9" width="6" height="6" rx="1" />
            <rect x="9" y="9" width="6" height="6" rx="1" />
        </svg>
    )
}
function MapIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="1,3 5,1 11,3 15,1 15,13 11,15 5,13 1,15" />
            <line x1="5" y1="1" x2="5" y2="13" />
            <line x1="11" y1="3" x2="11" y2="15" />
        </svg>
    )
}
function RadarIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5">
            <circle cx="8" cy="8" r="7" />
            <circle cx="8" cy="8" r="4" strokeOpacity=".5" />
            <circle cx="8" cy="8" r="1.5" fill={color} />
            <line x1="8" y1="8" x2="13" y2="3" strokeOpacity=".7" />
        </svg>
    )
}
function GraphIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round">
            <circle cx="8" cy="8" r="2.5" />
            <circle cx="2.5" cy="4" r="1.5" />
            <circle cx="13.5" cy="4" r="1.5" />
            <circle cx="2.5" cy="12" r="1.5" />
            <circle cx="13.5" cy="12" r="1.5" />
            <line x1="5.4" y1="6.6" x2="4" y2="5.4" />
            <line x1="10.6" y1="6.6" x2="12" y2="5.4" />
            <line x1="5.4" y1="9.4" x2="4" y2="10.6" />
            <line x1="10.6" y1="9.4" x2="12" y2="10.6" />
        </svg>
    )
}
function AlertIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M8 1L15 14H1L8 1Z" />
            <line x1="8" y1="6" x2="8" y2="9" />
            <circle cx="8" cy="11.5" r=".5" fill={color} />
        </svg>
    )
}
function SearchIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round">
            <circle cx="6.5" cy="6.5" r="5" />
            <line x1="10.5" y1="10.5" x2="14.5" y2="14.5" />
        </svg>
    )
}
function ShieldIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M8 1L14 4V8C14 11.3 11.3 14.4 8 15 4.7 14.4 2 11.3 2 8V4L8 1Z" />
        </svg>
    )
}
function LogoutIcon({ size, color }: { size: number; color: string }) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 2H13A1 1 0 0 1 14 3V13A1 1 0 0 1 13 14H10" />
            <line x1="7" y1="8" x2="1" y2="8" />
            <polyline points="4,5 1,8 4,11" />
        </svg>
    )
}
