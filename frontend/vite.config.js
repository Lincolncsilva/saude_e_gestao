// frontend/vite.config.js
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Carrega variáveis de ambiente
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    
    // ADICIONE ESTA SEÇÃO:
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '~': path.resolve(__dirname, './src') // opcional: ~ também
      }
    },
    
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          //rewrite: (path) => path.replace(/^\/api/, ''),
          secure: false
        }
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia']
          }
        }
      }
    },
    // Configuração para variáveis de ambiente no cliente
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || '/api')
    }
    // Adicione temporariamente no vite.config.js:
    

  }
  
})