/** Spectra — Badge (Palantir light theme) */
type BadgeColor = 'indigo' | 'blue' | 'teal' | 'amber' | 'rose' | 'slate' | 'cyan' | 'violet' | 'emerald'

const styles: Record<BadgeColor, string> = {
    indigo: 'background:#eef2ff;color:#4338ca;border:1px solid #c7d2fe',
    blue: 'background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe',
    teal: 'background:#f0fdfa;color:#0f766e;border:1px solid #99f6e4',
    amber: 'background:#fffbeb;color:#b45309;border:1px solid #fde68a',
    rose: 'background:#fef2f2;color:#b91c1c;border:1px solid #fecaca',
    slate: 'background:#f1f5f9;color:#475569;border:1px solid #e2e8f0',
    cyan: 'background:#ecfeff;color:#0e7490;border:1px solid #a5f3fc',
    violet: 'background:#f5f3ff;color:#6d28d9;border:1px solid #ddd6fe',
    emerald: 'background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0',
}

export default function Badge({ label, color = 'slate' }: { label: string; color?: BadgeColor }) {
    return (
        <span style={{
            ...Object.fromEntries(
                (styles[color] || styles.slate).split(';').map(s => {
                    const [k, ...v] = s.split(':')
                    return [k.trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase()), v.join(':').trim()]
                })
            ),
            display: 'inline-flex', alignItems: 'center',
            borderRadius: 20, padding: '2px 10px',
            fontSize: 11, fontWeight: 600, letterSpacing: '.03em',
        }}>
            {label}
        </span>
    )
}
