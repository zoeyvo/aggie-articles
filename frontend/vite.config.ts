import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [svelte()],  server: mode === 'development' ? {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying request:', req.url)
          })
        }
      },
      '/login': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/logout': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/auth': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      }
    },
  } : undefined,
}))
