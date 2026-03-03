/**
 * Spectra — RiskBadge Component
 * Displays a colored badge for a person's risk score (0–100).
 *
 * Score ranges:
 *   0–25   → LOW    (green)
 *   26–50  → MEDIUM (yellow)
 *   51–75  → HIGH   (orange)
 *   76–100 → CRITICAL (red)
 */

interface RiskBadgeProps {
    score: number | null | undefined
    showLabel?: boolean
    size?: 'sm' | 'md' | 'lg'
}

interface RiskLevel {
    label: string
    bg: string
    text: string
    ring: string
}

function getRiskLevel(score: number): RiskLevel {
    if (score <= 25) {
        return { label: 'LOW', bg: 'bg-emerald-500/20', text: 'text-emerald-400', ring: 'ring-emerald-500/40' }
    } else if (score <= 50) {
        return { label: 'MEDIUM', bg: 'bg-yellow-500/20', text: 'text-yellow-400', ring: 'ring-yellow-500/40' }
    } else if (score <= 75) {
        return { label: 'HIGH', bg: 'bg-orange-500/20', text: 'text-orange-400', ring: 'ring-orange-500/40' }
    } else {
        return { label: 'CRITICAL', bg: 'bg-red-500/20', text: 'text-red-400', ring: 'ring-red-500/40' }
    }
}

export default function RiskBadge({ score, showLabel = true, size = 'md' }: RiskBadgeProps) {
    if (score === null || score === undefined) {
        return (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-mono
                bg-slate-700/50 text-slate-500 ring-1 ring-slate-600/40">
                —
            </span>
        )
    }

    const { label, bg, text, ring } = getRiskLevel(score)

    const sizeClasses = {
        sm: 'px-1.5 py-0.5 text-xs gap-1',
        md: 'px-2.5 py-1 text-xs gap-1.5',
        lg: 'px-3 py-1.5 text-sm gap-2',
    }[size]

    return (
        <span
            className={`inline-flex items-center ${sizeClasses} rounded-full font-mono font-semibold
                ${bg} ${text} ring-1 ${ring} transition-all`}
            title={`Risk score: ${score.toFixed(1)}/100`}
        >
            <span className="tabular-nums">{score.toFixed(0)}</span>
            {showLabel && <span className="opacity-80 font-bold">{label}</span>}
        </span>
    )
}
