/**
 * Spectra — EthicsBanner
 *
 * Non-dismissible warning banner shown at the top of EVERY page.
 * ⚠️ This component must NEVER be removed or made dismissible.
 * It is a first-class ethics requirement of the Spectra project.
 */

export default function EthicsBanner() {
    return (
        <div
            role="banner"
            aria-label="Synthetic data warning"
            style={{ height: 'var(--ethics-banner-height, 52px)' }}
            className="
        fixed top-0 left-0 right-0 z-50
        flex items-center justify-center gap-3
        bg-gradient-to-r from-amber-900/90 via-amber-800/90 to-amber-900/90
        border-b border-amber-500/50
        backdrop-blur-sm px-4 py-2
      "
        >
            {/* Warning icon */}
            <span className="text-amber-400 text-xl flex-shrink-0" aria-hidden="true">
                ⚠️
            </span>

            {/* Main message */}
            <p className="text-amber-100 text-sm font-semibold tracking-wide text-center leading-tight">
                <span className="text-amber-300 font-bold">SPECTRA — SYNTHETIC DATA ONLY.</span>
                {' '}This tool does not monitor real people.
                {' '}All data is computer-generated for educational purposes.
            </p>

            {/* Badge */}
            <span
                className="
          hidden sm:inline-flex flex-shrink-0
          px-2 py-0.5 rounded-full text-xs font-bold
          bg-amber-500/20 text-amber-300 border border-amber-500/40
        "
            >
                NOT REAL SURVEILLANCE
            </span>
        </div>
    )
}
