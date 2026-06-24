import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  // The proxy always targets the local backend.
  // VITE_API_BASE_URL is only relevant when building for a deployed
  // (cross-origin) backend; in that case the proxy is bypassed because
  // client.ts uses an absolute URL and requests don't hit the dev server.
  const backendTarget = 'http://localhost:8000';

  // For deployed builds, VITE_API_BASE_URL is baked in at build time via
  // import.meta.env.VITE_API_BASE_URL — no proxy is involved.
  void env; // silence unused-var lint for env

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
      proxy: {
        // All /api/* and /health requests are proxied server-side to the
        // backend. Because the proxy runs on the Vite server (not in the
        // browser), this works for any client reaching the Vite network URL
        // (e.g. http://192.168.x.x:5173) without CORS or localhost issues.
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/health': {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
  };
});
