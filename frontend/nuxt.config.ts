// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/ui'],
  css: ['~/src/app/assets/main.css'],
  dir: {
      pages: './src/app/routes',
      layouts: './src/app/layouts'
    }
})
