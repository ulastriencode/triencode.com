import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 3000,
    resolve: {
      alias: {
        // eslint-disable-next-line no-undef
        '@': path.resolve(__dirname, './src'),
      },
    proxy: {
      "/api": {
        // Hedef önemli değil, router zaten tenant'a göre döndürüyor
        target: "http://127.0.0.1:8000",
        // EN KRİTİK SATIR: Host header'ını aynen koru
        changeOrigin: false,
        // Hangi backend'e gideceğini host'a göre seç
        router: (req) => {
          const h = req.headers.host || ""; // firma1.localhost:3000 / firma2.localhost:3000
          return `http://${h.replace(":3000", ":8000")}`; // firmaX.localhost:8000
        },
      },
    },
  },
}});
