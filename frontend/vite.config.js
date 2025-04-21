import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '^/backend/.*': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
}) 