/**
 * Spectra — TimeScrubber (Palantir light theme)
 * Light white panel docked at map bottom.
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import type { HistoryEntry } from '../../types/telemetry'

interface TimeScrubberProps {
    history: HistoryEntry[]
    onScrub: (entry: HistoryEntry | null) => void
    isLive: boolean
}

const SPEEDS = [1, 2, 5] as const
type Speed = typeof SPEEDS[number]

function fmtTime(epochSec: number): string {
    return new Date(epochSec * 1000).toLocaleTimeString([], {
        hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
}

export default function TimeScrubber({ history, onScrub, isLive }: TimeScrubberProps) {
    const [playing, setPlaying] = useState(false)
    const [scrubIndex, setScrubIndex] = useState(0)
    const [speed, setSpeed] = useState<Speed>(1)
    const playTimer = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => {
        if (isLive) setScrubIndex(Math.max(0, history.length - 1))
    }, [history.length, isLive])

    const stopPlay = useCallback(() => {
        if (playTimer.current) { clearInterval(playTimer.current); playTimer.current = null }
        setPlaying(false)
    }, [])

    const goLive = useCallback(() => {
        stopPlay()
        setScrubIndex(Math.max(0, history.length - 1))
        onScrub(null)
    }, [history.length, onScrub, stopPlay])

    const startPlay = useCallback(() => {
        if (history.length === 0) return
        setPlaying(true)
        playTimer.current = setInterval(() => {
            setScrubIndex(prev => {
                const next = prev + 1
                if (next >= history.length) {
                    clearInterval(playTimer.current!); playTimer.current = null
                    setPlaying(false); onScrub(null)
                    return history.length - 1
                }
                onScrub(history[next]); return next
            })
        }, 1000 / speed)
    }, [history, onScrub, speed])

    useEffect(() => {
        if (playing) { stopPlay(); startPlay() }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [speed])

    useEffect(() => () => stopPlay(), [stopPlay])

    const handleSlider = (idx: number) => {
        stopPlay(); setScrubIndex(idx)
        const entry = history[idx]
        if (entry) onScrub(entry)
    }

    const total = Math.max(history.length - 1, 1)
    const currentTs = history[scrubIndex]?.timestamp ?? null

    const btn = (active: boolean, onClick: () => void, children: React.ReactNode, title?: string) => (
        <button
            onClick={onClick}
            title={title}
            style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5,
                padding: '5px 12px', borderRadius: 5,
                background: active ? '#4f46e5' : '#f8f9fb',
                border: `1px solid ${active ? '#4338ca' : '#e2e8f0'}`,
                color: active ? '#fff' : '#475569',
                fontSize: 12, fontWeight: 600, cursor: 'pointer',
                transition: 'all .12s',
            }}
        >{children}</button>
    )

    return (
        <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            background: 'rgba(255,255,255,0.97)',
            backdropFilter: 'blur(12px)',
            borderTop: '1px solid #e2e8f0',
            padding: '8px 16px',
            display: 'flex', alignItems: 'center', gap: 12,
            zIndex: 1000,
            boxShadow: '0 -2px 8px rgba(15,23,42,.07)',
            fontFamily: 'Inter, system-ui, sans-serif',
        }}>
            {/* Play/Pause */}
            {btn(playing, playing ? stopPlay : startPlay,
                playing
                    ? <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><rect x="1" y="1" width="3" height="8" /><rect x="6" y="1" width="3" height="8" /></svg>
                    : <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><polygon points="1,1 9,5 1,9" /></svg>,
                playing ? 'Pause replay' : 'Play replay'
            )}

            {/* Timestamp */}
            <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono, monospace', color: '#475569', minWidth: 80 }}>
                {currentTs ? fmtTime(currentTs) : '--:--:--'}
            </span>

            {/* Slider */}
            <input
                type="range" min={0} max={total} value={scrubIndex}
                onChange={e => handleSlider(Number(e.target.value))}
                style={{ flex: 1, accentColor: '#4f46e5', cursor: 'pointer' }}
                title="Scrub through history"
            />

            <span style={{ fontSize: 11, color: '#94a3b8', whiteSpace: 'nowrap' }}>
                {history.length} frames
            </span>

            {/* Speed */}
            <div style={{ display: 'flex', gap: 4 }}>
                {SPEEDS.map(s => btn(speed === s, () => setSpeed(s), `${s}×`))}
            </div>

            {/* Live button */}
            <button
                onClick={goLive}
                style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '5px 12px', borderRadius: 5, whiteSpace: 'nowrap',
                    background: isLive ? '#f0fdf4' : '#f8f9fb',
                    border: `1px solid ${isLive ? '#bbf7d0' : '#e2e8f0'}`,
                    color: isLive ? '#15803d' : '#94a3b8',
                    fontSize: 12, fontWeight: 700, cursor: 'pointer',
                }}
            >
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: isLive ? '#22c55e' : '#94a3b8', flexShrink: 0 }} />
                LIVE
            </button>
        </div>
    )
}
