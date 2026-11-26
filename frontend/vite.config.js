import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { reidServer } from './reidServer.js'

export default defineConfig({
  plugins: [vue(), reidServer()],
  server: {
    watch: { ignored: ['**/public/tracking.json', '**/public/.cap28-session-*.tmp'] }
  }
})
