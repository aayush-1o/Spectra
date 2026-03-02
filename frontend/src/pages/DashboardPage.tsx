/**
 * Spectra — Placeholder Dashboard Page
 * Shows the ethics banner and a "coming soon" skeleton.
 * Will be replaced with real KPI cards and charts in Phase 4.
 */

import EthicsBanner from '../components/layout/EthicsBanner'

export default function DashboardPage() {
    return (
        <>
            <EthicsBanner />

            <main className="page-content min-h-screen bg-[#0a0f1e] text-slate-100">
                {/* Hero */}
                <section className="flex flex-col items-center justify-center py-24 px-6 text-center gap-6">
                    {/* Logo / Title */}
                    <div className="flex items-center gap-3 mb-4">
                        <span className="text-5xl">🔭</span>
                        <h1 className="text-5xl font-black tracking-tight bg-gradient-to-r from-cyan-400 to-violet-500 bg-clip-text text-transparent">
                            Spectra
                        </h1>
                    </div>

                    <p className="text-slate-400 text-lg max-w-xl">
                        Synthetic Intelligence &amp; Movement Simulation for Analytics Training
                    </p>

                    {/* Status pill */}
                    <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-900/40 border border-violet-500/30 text-violet-300 text-sm font-medium">
                        <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
                        Phase 1 — Core Setup in progress
                    </span>

                    {/* Coming-soon cards skeleton */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-10 w-full max-w-3xl">
                        {['Dashboard', 'Map View', 'Graph View'].map((label) => (
                            <div
                                key={label}
                                className="
                  rounded-xl border border-slate-700/50 bg-slate-800/30
                  p-6 flex flex-col items-center gap-3
                  animate-pulse
                "
                            >
                                <div className="w-10 h-10 rounded-full bg-slate-700" />
                                <div className="h-4 w-24 rounded bg-slate-700" />
                                <p className="text-xs text-slate-500 mt-1">{label} — coming in Phase 4</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Ethics footer note */}
                <footer className="text-center py-8 text-slate-600 text-xs">
                    ⚠️ All data shown in Spectra is 100% synthetic and computer-generated.
                    No real people are tracked.
                </footer>
            </main>
        </>
    )
}
