interface PaginationProps {
    offset: number
    limit: number
    hasMore: boolean
    onPrev: () => void
    onNext: () => void
}

export default function Pagination({ offset, limit, hasMore, onPrev, onNext }: PaginationProps) {
    const page = Math.floor(offset / limit) + 1
    return (
        <div className="flex items-center justify-between py-4">
            <button
                onClick={onPrev}
                disabled={offset === 0}
                className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-sm
                   disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
            >
                ← Prev
            </button>
            <span className="text-xs text-slate-500">Page {page}</span>
            <button
                onClick={onNext}
                disabled={!hasMore}
                className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-sm
                   disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
            >
                Next →
            </button>
        </div>
    )
}
