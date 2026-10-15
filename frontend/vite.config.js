import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// WHY THIS FILE EXISTS:
// Vite's dev server proxies /api requests to the backend so the browser
// never knows the backend hostname. In production, Nginx does the same job.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
