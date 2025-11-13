import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Questo permette di eseguire Vite nel container
    host: '0.0.0.0', 
    // La porta 3000 è quella che abbiamo mappato in docker-compose.yml
    port: 3000, 
    // Abilita l'hot-reloading
    watch: {
      usePolling: true,
    },
  },
})
