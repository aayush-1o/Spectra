/**
 * Spectra — Ethics Banner
 * Fixed at top. Non-dismissible. Visible on every page.
 */
export default function EthicsBanner() {
    return (
        <div
            className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 px-4 py-2.5 text-center text-xs font-semibold"
            style={{ background: 'linear-gradient(90deg, #7c3aed 0%, #0ea5e9 100%)', color: '#fff', minHeight: '44px' }}
        >
            <span>⚠️</span>
            <span>
                SYNTHETIC DATA ONLY — Spectra uses 100% computer-generated data.
                No real people are tracked or surveilled. Educational use only.
            </span>
            <span>⚠️</span>
        </div>
    )
}
