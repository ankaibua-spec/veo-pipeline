import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig(async () => ({
  plugins: [react(), tailwindcss()],
  clearScreen: false,
  server: {
    port: 3000,
    strictPort: true,
    host: '0.0.0.0',
    hmr: { protocol: 'ws', host: 'localhost', port: 3001 },
    watch: { ignored: ['**/src-tauri/**'] },
  },
  envPrefix: ['VITE_', 'TAURI_'],
  resolve: {
    alias: { '@': path.resolve(__dirname, '.') },
  },
}));
