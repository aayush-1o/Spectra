/**
 * Spectra — KPI Card (Palantir light theme)
 */

interface KpiCardProps {
    icon: React.ReactNode
    label: string
    value: number | string | null
    loading?: boolean
    color?: 'indigo' | 'blue' | 'teal' | 'amber' | 'rose'
    delta?: string
}

const palette = {
    indigo: { bar: '#4f46e5', bg: '#eef2ff', text: '#4338ca' },
    blue: { bar: '#2563eb', bg: '#eff6ff', text: '#1d4ed8' },
    teal: { bar: '#0d9488', bg: '#f0fdfa', text: '#0f766e' },
    amber: { bar: '#d97706', bg: '#fffbeb', text: '#b45309' },
    rose: { bar: '#dc2626', bg: '#fef2f2', text: '#b91c1c' },
}

export default function KpiCard({ icon, label, value, loading, color = 'indigo', delta }: KpiCardProps) {
    const p = palette[color]
    return (
        <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '18px 20px',
            boxShadow: 'var(--shadow-sm)',
            position: 'relative',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
        }}>
            {/* Accent bar */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: p.bar }} />

            {/* Label row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '.06em', textTransform: 'uppercase' }}>
                    {label}
                </span>
                <span style={{
                    width: 30, height: 30, borderRadius: 6,
                    background: p.bg, color: p.text,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 14,
                }}>
                    {icon}
                </span>
            </div>

            {/* Value */}
            {loading ? (
                <div style={{ height: 32, width: 80, borderRadius: 4, background: '#e2e8f0', animation: 'pulse 1.5s infinite' }} />
            ) : (
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <span style={{ fontSize: 32, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                        {value ?? '—'}
                    </span>
                    {delta && (
                        <span style={{ fontSize: 12, fontWeight: 500, color: p.text }}>
                            {delta}
                        </span>
                    )}
                </div>
            )}
        </div>
    )
}
