import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// import electron from 'vite-plugin-electron'  // Temporarily disabled for web-only dev
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Temporarily disabled electron plugin for web-only development
    // electron([
    //   {
    //     // Main process entry point
    //     entry: 'electron/main.ts',
    //   },
    // ]),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
  },
})
