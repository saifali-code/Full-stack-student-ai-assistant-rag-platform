// frontend/vite.config.js
// Vite is the build tool that runs our React app in development

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,  // Our frontend runs on http://localhost:5173
  },
})