export type AuthUser = {
  id: string
  email: string
  name: string
  role: 'user' | 'approver'
}

export function useAuth() {
  const config = useRuntimeConfig()
  const user = useState<AuthUser | null>('auth.user', () => null)
  const loaded = useState('auth.loaded', () => false)

  async function refresh() {
    try {
      user.value = await $fetch<AuthUser>('/auth/me', {
        baseURL: config.public.apiBase,
        credentials: 'include'
      })
    } catch {
      user.value = null
    } finally {
      loaded.value = true
    }
  }

  function login() {
    window.location.assign(new URL('/auth/microsoft/login', config.public.apiBase).href)
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
