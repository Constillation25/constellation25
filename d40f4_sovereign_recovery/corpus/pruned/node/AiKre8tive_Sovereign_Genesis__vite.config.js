// REPO: ARC.AI_Sovereign_Genesis | FILE: vite.config.js | CONSTELLATION25

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  }
})
