/**
 * Spectra — useDebounce hook
 * Phase 5: Delays updating a value until `delay` ms have elapsed without
 * a new value arriving.  Used for search inputs to prevent firing an API
 * request on every keypress.
 *
 * Usage:
 *   const debouncedSearch = useDebounce(searchTerm, 300)
 *   // only changes 300ms after the user stops typing
 */
import { useEffect, useState } from 'react'

export function useDebounce<T>(value: T, delay: number = 300): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value)

    useEffect(() => {
        const timer = setTimeout(() => setDebouncedValue(value), delay)
        return () => clearTimeout(timer)
    }, [value, delay])

    return debouncedValue
}
