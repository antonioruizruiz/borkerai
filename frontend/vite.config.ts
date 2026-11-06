import path from 'node:path'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    // El proyecto vive en /mnt/d (disco de Windows montado en WSL2): ahí no
    // llegan los avisos automáticos de "este archivo ha cambiado" (inotify),
    // así que Vite tiene que comprobar los archivos a intervalos (polling).
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
})
