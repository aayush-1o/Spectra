interface KpiCardProps {
    icon: string
    label: string
    value: number | string | null
    loading?: boolean
    color?: 'cyan' | 'violet' | 'amber' | 'emerald' | 'rose'
}

const colors = {
    cyan: { border: 'border-cyan-500/30', icon: 'text-cyan-400', val: 'text-cyan-300' },
    violet: { border: 'border-violet-500/30', icon: 'text-violet-400', val: 'text-violet-300' },
    amber: { border: 'border-amber-500/30', icon: 'text-amber-400', val: 'text-amber-300' },
    emerald: { border: 'border-emerald-500/30', icon: 'text-emerald-400', val: 'text-emerald-300' },
    rose: { border: 'border-rose-500/30', icon: 'text-rose-400', val: 'text-rose-300' },
}

export default function KpiCard({ icon, label, value, loading, color = 'cyan' }: KpiCardProps) {
    const c = colors[color]
    return (
        <div className={`rounded-xl border ${c.border} bg-slate-800/40 p-5 flex flex-col gap-2`}>
            <div className="flex items-center gap-2">
                <span className={`text-2xl ${c.icon}`}>{icon}</span>
                <span className="text-sm text-slate-400 font-medium">{label}</span>
            </div>
            {loading ? (
                <div className="h-8 w-24 rounded bg-slate-700 animate-pulse" />
            ) : (
                <span className={`text-3xl font-black ${c.val}`}>
                    {value ?? '—'}
                </span>
            )}
        </div>
    )
}
