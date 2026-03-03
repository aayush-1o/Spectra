import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Cesium's pre-built static assets directory
const cesiumBuild = path.join(__dirname, 'node_modules', 'cesium', 'Build', 'Cesium')

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // Copy Cesium's static files so its web workers can resolve at runtime
    viteStaticCopy({
      targets: [
        { src: `${cesiumBuild}/Workers/**/*`, dest: 'cesium/Workers' },
        { src: `${cesiumBuild}/ThirdParty/**/*`, dest: 'cesium/ThirdParty' },
        { src: `${cesiumBuild}/Assets/**/*`, dest: 'cesium/Assets' },
        { src: `${cesiumBuild}/Widgets/**/*`, dest: 'cesium/Widgets' },
      ],
    }),
  ],
  define: {
    // Tell Cesium where to load its web workers from (must match viteStaticCopy dest)
    CESIUM_BASE_URL: JSON.stringify('/cesium'),
  },
  resolve: {
    alias: {
      cesium: path.resolve(__dirname, 'node_modules', 'cesium'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    css: false,
  },
})
