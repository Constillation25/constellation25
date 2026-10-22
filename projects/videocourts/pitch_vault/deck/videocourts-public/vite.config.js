import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: { vendor: ['react', 'react-dom'] }
      }
    }
  },
  server: {
    proxy: {
      '/ws':  { target: 'ws://localhost:8080',  ws: true },
      '/api': { target: 'http://localhost:8080', changeOrigin: true }
    }
  }
})
