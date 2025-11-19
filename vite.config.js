import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/rankings': 'http://localhost:8000',
      '/team': 'http://localhost:8000',
      '/clear-cache': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})