/**
 * Spectra — useAssetStream hook  (Phase 9)
 *
 * Manages the WebSocket connection to /api/v1/stream/assets.
 * Features:
 *  - Auto-reconnect with exponential back-off (max 30s)
 *  - Parses manifest + position frames
 *  - Maintains a rolling history buffer (MAX_HISTORY_SECONDS) for the time scrubber
 *  - Exposes current positions, connection state, and history
 *
 * ⚠️ All data is 100% synthetic — no real aircraft or vehicle data.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import type { AssetManifest, AssetPosition, HistoryEntry } from '../types/telemetry'

const MAX_HISTORY_SECONDS = 120   // keep last 2 minutes of positions
const MIN_BACKOFF_MS = 1_000
const MAX_BACKOFF_MS = 30_000

interface UseAssetStreamResult {
    /** Current live positions keyed by asset id */
    positions: Record<string, AssetPosition>
    /** Flat list of current positions (convenience) */
    assetList: AssetPosition[]
    /** All known assets from manifest */
    manifest: AssetManifest[]
    /** True when WebSocket is open and receiving data */
    connected: boolean
    /** Last error message, if any */
    error: string | null
    /** Rolling history buffer for time scrubber */
    history: HistoryEntry[]
}

export function useAssetStream(wsUrl: string): UseAssetStreamResult {
    const [positions, setPositions] = useState<Record<string, AssetPosition>>({})
    const [manifest, setManifest] = useState<AssetManifest[]>([])
    const [connected, setConnected] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [history, setHistory] = useState<HistoryEntry[]>([])

    const wsRef = useRef<WebSocket | null>(null)
    const backoffRef = useRef(MIN_BACKOFF_MS)
    const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
    const isMounted = useRef(true)

    const connect = useCallback(() => {
        if (!isMounted.current) return
        try {
            const ws = new WebSocket(wsUrl)
            wsRef.current = ws

            ws.onopen = () => {
                if (!isMounted.current) return
                setConnected(true)
                setError(null)
                backoffRef.current = MIN_BACKOFF_MS   // reset back-off on successful connection
            }

            ws.onmessage = (ev: MessageEvent<string>) => {
                if (!isMounted.current) return
                try {
                    const msg = JSON.parse(ev.data)

                    if (msg.type === 'manifest') {
                        setManifest(msg.assets as AssetManifest[])

                    } else if (msg.type === 'positions') {
                        const incoming = msg.data as AssetPosition[]
                        const next: Record<string, AssetPosition> = {}
                        for (const pos of incoming) {
                            next[pos.id] = pos
                        }
                        setPositions(next)

                        // Append to history buffer, trimming entries older than MAX_HISTORY_SECONDS
                        const now = Date.now() / 1000
                        setHistory(prev => {
                            const entry: HistoryEntry = { timestamp: now, positions: next }
                            const cutoff = now - MAX_HISTORY_SECONDS
                            return [...prev.filter(h => h.timestamp >= cutoff), entry]
                        })
                    }
                } catch {
                    // Silently ignore malformed frames
                }
            }

            ws.onerror = () => {
                if (!isMounted.current) return
                setError('WebSocket connection error — retrying…')
                setConnected(false)
            }

            ws.onclose = () => {
                if (!isMounted.current) return
                setConnected(false)
                wsRef.current = null
                // Exponential back-off reconnect
                const delay = backoffRef.current
                backoffRef.current = Math.min(delay * 2, MAX_BACKOFF_MS)
                retryTimer.current = setTimeout(connect, delay)
            }
        } catch (err) {
            setError(`Failed to open WebSocket: ${err}`)
            const delay = backoffRef.current
            backoffRef.current = Math.min(delay * 2, MAX_BACKOFF_MS)
            retryTimer.current = setTimeout(connect, delay)
        }
    }, [wsUrl])

    useEffect(() => {
        isMounted.current = true
        connect()
        return () => {
            isMounted.current = false
            if (retryTimer.current) clearTimeout(retryTimer.current)
            if (wsRef.current) {
                wsRef.current.onclose = null   // prevent reconnect on intentional unmount
                wsRef.current.close()
            }
        }
    }, [connect])

    const assetList = Object.values(positions)

    return { positions, assetList, manifest, connected, error, history }
}
