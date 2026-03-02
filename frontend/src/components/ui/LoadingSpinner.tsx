export default function LoadingSpinner({ size = 40 }: { size?: number }) {
    return (
        <div className="flex items-center justify-center w-full py-12">
            <svg
                width={size}
                height={size}
                viewBox="0 0 24 24"
                fill="none"
                className="animate-spin"
            >
                <circle cx="12" cy="12" r="10" stroke="#334155" strokeWidth="3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="#7c3aed" strokeWidth="3" strokeLinecap="round" />
            </svg>
        </div>
    )
}
