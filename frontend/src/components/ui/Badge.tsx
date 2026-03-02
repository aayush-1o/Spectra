type BadgeColor = 'cyan' | 'violet' | 'amber' | 'rose' | 'emerald' | 'slate'

const styles: Record<BadgeColor, string> = {
    cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
    violet: 'bg-violet-500/15 text-violet-300 border-violet-500/30',
    amber: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    rose: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    emerald: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    slate: 'bg-slate-700/40 text-slate-300 border-slate-600/40',
}

export default function Badge({ label, color = 'slate' }: { label: string; color?: BadgeColor }) {
    return (
        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${styles[color]}`}>
            {label}
        </span>
    )
}
