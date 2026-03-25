import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import devFilesPlugin from './vite-plugin-dev-files.js'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), devFilesPlugin()],
  server: {
    port: 5173,
    strictPort: false,
    host: true,
  },
})
