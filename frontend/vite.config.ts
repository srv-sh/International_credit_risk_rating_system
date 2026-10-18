import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Dev proxy, so the browser only talks to the Vite origin (no CORS):
//   /api -> compute API (api/, port 8002)
//   /db  -> storage API (db_api/, port 8001)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8002', changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, '') },
      '/db': { target: 'http://localhost:8001', changeOrigin: true, rewrite: (p) => p.replace(/^\/db/, '') },
    },
  },
})
