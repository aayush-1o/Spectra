/**
 * Spectra — App Layout (light theme)
 */
import type { ReactNode } from 'react'
import EthicsBanner from './EthicsBanner'
import Sidebar from './Sidebar'

export default function Layout({ children }: { children: ReactNode }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-base)' }}>
            <EthicsBanner />
            <div style={{ display: 'flex', flex: 1, marginTop: 'var(--ethics-banner-height)', overflow: 'hidden' }}>
                <Sidebar />
                <main style={{ flex: 1, overflowY: 'auto', padding: '28px 32px', color: 'var(--text-primary)' }}>
                    {children}
                </main>
            </div>
        </div>
    )
}
