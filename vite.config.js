import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/rankings': 'http://localhost:8000',
      '/team': 'http://localhost:8000',
      '/clear-cache': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})