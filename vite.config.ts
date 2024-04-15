import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
 
export default defineConfig({
  server: {
    proxy: {
      '/api': {
           target: 'http://localhost:3001',
           changeOrigin: true,
           secure: false,      
           ws: true,
      },
    },
    port: 3002,
    open: true,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})