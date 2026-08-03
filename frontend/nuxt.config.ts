import { fileURLToPath } from 'node:url'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  },
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/ui'],
  css: ['@/app/styles/main.css'],
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'
    }
  },
  dir: {
    pages: './src/app/routes',
    layouts: './src/app/layouts',
    middleware: './src/app/routing'
  }
})
