import type { UserDTO } from '@/shared/api'

export type AuthUser = UserDTO

export function useAuth() {
  const config = useRuntimeConfig()
  const requestHeaders = useRequestHeaders(['cookie'])
  const user = useState<AuthUser | null>('auth.user', () => null)
  const loaded = useState('auth.loaded', () => false)

  async function refresh() {
    try {
      user.value = await $fetch<AuthUser>('/auth/me', {
        baseURL: config.public.apiBase,
        credentials: 'include',
        headers: requestHeaders
      })
    } catch {
      user.value = null
    } finally {
      loaded.value = true
    }
  }

  function login() {
    window.location.assign(`${config.public.apiBase}/auth/microsoft/login`)
  }

  async function logout() {
    await $fetch('/auth/logout', {
      baseURL: config.public.apiBase,
      method: 'POST',
      credentials: 'include'
    })
    user.value = null
    await navigateTo('/login')
  }

  return { user, loaded, refresh, login, logout }
}
