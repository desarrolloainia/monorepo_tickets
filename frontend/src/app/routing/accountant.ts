import { useAuth } from '@/shared/auth'

export default defineNuxtRouteMiddleware(() => {
  const { user } = useAuth()
  if (user.value?.role !== 'accountant') return navigateTo('/')
})
