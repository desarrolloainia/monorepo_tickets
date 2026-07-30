import { useAuth } from '~/src/shared/auth'

export default defineNuxtRouteMiddleware(async () => {
  const { loaded, refresh, user } = useAuth()

  if (!loaded.value) await refresh()
  if (!user.value) return navigateTo('/login')
})
