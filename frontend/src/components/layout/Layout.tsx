/**
 * Spectra — App Layout
 * Combines EthicsBanner + Sidebar + page content.
 */
import type { ReactNode } from 'react'
import EthicsBanner from './EthicsBanner'
import Sidebar from './Sidebar'

export default function Layout({ children }: { children: ReactNode }) {
    return (
        <div className="flex h-screen overflow-hidden" style={{ background: '#0a0f1e' }}>
            {/* Fixed ethics banner across the full top */}
            <EthicsBanner />

            {/* Sidebar + main content below banner */}
            <div className="flex w-full" style={{ marginTop: '44px', height: 'calc(100vh - 44px)' }}>
                <Sidebar />
                <main className="flex-1 overflow-y-auto p-6 text-slate-100">
                    {children}
                </main>
            </div>
        </div>
    )
}
