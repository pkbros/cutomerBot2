import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config: React plugin + fixed dev port.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
