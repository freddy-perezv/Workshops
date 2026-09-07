import path from 'node:path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const mockMode = process.env.VITE_MOCK_MODE === 'true';

export default defineConfig({
  root: __dirname,
  plugins: [react()],
  server: mockMode ? { port: 5173 } : { middlewareMode: true },
  build: {
    outDir: path.resolve(__dirname, './dist'),
    emptyOutDir: true,
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react/jsx-dev-runtime', 'react/jsx-runtime'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
