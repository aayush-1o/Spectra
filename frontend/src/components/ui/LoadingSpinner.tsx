/** Spectra — Loading Spinner (light theme) */
export default function LoadingSpinner({ size = 36 }: { size?: number }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', padding: '48px 0' }}>
            <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className="animate-spin">
                <circle cx="12" cy="12" r="10" stroke="#e2e8f0" strokeWidth="3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="#4f46e5" strokeWidth="3" strokeLinecap="round" />
            </svg>
        </div>
    )
}
