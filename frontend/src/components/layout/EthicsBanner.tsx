/** Spectra — Ethics Banner (light theme) */
export default function EthicsBanner() {
    return (
        <div
            style={{
                position: 'fixed', top: 0, left: 0, right: 0, zIndex: 60,
                height: 'var(--ethics-banner-height)',
                background: '#0f172a',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                gap: 8, padding: '0 16px',
                fontSize: 11, fontWeight: 600, letterSpacing: '.04em',
                color: '#94a3b8',
                borderBottom: '1px solid #1e293b',
            }}
        >
            <span style={{ color: '#f59e0b' }}>▲</span>
            <span>
                SYNTHETIC DATA ONLY — All data is 100% computer-generated.
                No real people are tracked or surveilled.
            </span>
            <span style={{ color: '#f59e0b' }}>▲</span>
        </div>
    )
}
