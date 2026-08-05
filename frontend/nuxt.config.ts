// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/ui'],
  srcDir: 'src',
  css: ['@/app/styles/main.css'],
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'
    }
  },
  routeRules: {
    '/backend/**': {
      proxy: 'http://api:8000/**'
    }
  },
  dir: {
    pages: 'app/routes',
    layouts: 'app/layouts',
    middleware: 'app/routing'
  }
})
