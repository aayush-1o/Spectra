/**
 * Spectra — Performance Measurement Utility
 * Phase 5: Lightweight wrapper around console.time/timeEnd.
 *
 * - All measurements are dev-only (silenced in production).
 * - measureAsync wraps any async function; measureSync wraps synchronous ones.
 * - Designed for spotting slow renders and API calls during development.
 *
 * Usage:
 *   const data = await measureAsync('fetchPersons', () => api.getPersons())
 *   const result = measureSync('buildMatrix', () => heavyComputation())
 */

const IS_DEV = import.meta.env.DEV;

/**
 * Wrap an async function and log its wall-clock time in the browser console.
 * Returns the resolved value unchanged so it can be dropped in transparently.
 */
export async function measureAsync<T>(
    label: string,
    fn: () => Promise<T>
): Promise<T> {
    if (!IS_DEV) return fn();
    console.time(`⏱  ${label}`);
    try {
        const result = await fn();
        return result;
    } finally {
        console.timeEnd(`⏱  ${label}`);
    }
}

/**
 * Wrap a synchronous function and log its wall-clock time in the browser console.
 */
export function measureSync<T>(label: string, fn: () => T): T {
    if (!IS_DEV) return fn();
    console.time(`⏱  ${label}`);
    try {
        const result = fn();
        return result;
    } finally {
        console.timeEnd(`⏱  ${label}`);
    }
}

/**
 * Mark a component render in the Performance tab (dev only).
 * Call at the top level of a component body.
 */
export function markRender(componentName: string): void {
    if (!IS_DEV || !performance?.mark) return;
    performance.mark(`render:${componentName}`);
}
