import { computed, onScopeDispose, shallowRef, watch } from 'vue'

import type { BlockedUserDTO, MicrosoftUserDTO } from '@/shared/api'
import {
  blockMicrosoftUser,
  fetchBlockedUsers,
  searchMicrosoftUsers,
  unblockMicrosoftUser
} from '../api/blocked-users'

export function useBlockedUsers() {
  const config = useRuntimeConfig()
  const router = useRouter()
  const headers = useRequestHeaders(['cookie'])
  const options = { baseURL: config.public.apiBase, headers }
  const query = shallowRef('')
  const results = shallowRef<MicrosoftUserDTO[]>([])
  const searchError = shallowRef('')
  const searching = shallowRef(false)
  const hasSearched = shallowRef(false)
  const searchedQuery = shallowRef('')
  const notice = shallowRef('')
  const mutationError = shallowRef('')
  const pendingIds = shallowRef(new Set<string>())
  let searchTimer: ReturnType<typeof setTimeout> | undefined
  let searchSequence = 0
  const { data: blockedUsers, error, refresh, status } = useAsyncData(
    'blocked-users',
    () => fetchBlockedUsers(options),
    { default: () => [] }
  )

  watch(query, (nextQuery) => {
    clearTimeout(searchTimer)
    const request = ++searchSequence
    const value = nextQuery.trim()
    searchError.value = ''

    if (value.length < 2) {
      results.value = []
      searchedQuery.value = ''
      hasSearched.value = false
      searching.value = false
      return
    }

    hasSearched.value = true
    searching.value = true
    searchTimer = setTimeout(() => void runSearch(value, request), 300)
  })

  onScopeDispose(() => clearTimeout(searchTimer))

  async function errorDetail(cause: unknown, fallback: string) {
    const error = cause as { data?: { detail?: string }, statusCode?: number }
    if (error.statusCode === 401) {
      await router.push('/login')
      return ''
    }
    return error.data?.detail ?? fallback
  }

  async function search() {
    clearTimeout(searchTimer)
    const value = query.value.trim()
    if (value.length < 2) {
      searchError.value = 'Escribe al menos dos caracteres.'
      return
    }

    const request = ++searchSequence
    hasSearched.value = true
    searching.value = true
    await runSearch(value, request)
  }

  async function runSearch(value: string, request: number) {
    searchError.value = ''
    searchedQuery.value = value
    try {
      const users = await searchMicrosoftUsers(value, options)
      if (request === searchSequence) results.value = users
    } catch (cause) {
      if (request === searchSequence) {
        results.value = []
        searchError.value = String(await errorDetail(cause, 'No se pudo consultar Microsoft 365.'))
      }
    } finally {
      if (request === searchSequence) searching.value = false
    }
  }

  async function block(user: MicrosoftUserDTO) {
    await mutate(user.microsoft_oid, async () => {
      const blocked = await blockMicrosoftUser(user.microsoft_oid, options)
      blockedUsers.value = [...blockedUsers.value.filter(
        item => item.microsoft_oid !== blocked.microsoft_oid
      ), blocked].sort((a, b) => a.name.localeCompare(b.name, 'es'))
      results.value = results.value.map(item => item.microsoft_oid === user.microsoft_oid
        ? { ...item, blocked: true }
        : item)
      notice.value = `${user.name} ya no puede acceder a la aplicación.`
    })
  }

  async function unblock(user: BlockedUserDTO) {
    await mutate(user.microsoft_oid, async () => {
      await unblockMicrosoftUser(user.microsoft_oid, options)
      blockedUsers.value = blockedUsers.value.filter(
        item => item.microsoft_oid !== user.microsoft_oid
      )
      results.value = results.value.map(item => item.microsoft_oid === user.microsoft_oid
        ? { ...item, blocked: false }
        : item)
      notice.value = `${user.name} puede volver a acceder.`
    })
  }

  async function mutate(id: string, action: () => Promise<void>) {
    notice.value = ''
    mutationError.value = ''
    pendingIds.value = new Set(pendingIds.value).add(id)
    try {
      await action()
    } catch (cause) {
      mutationError.value = String(await errorDetail(cause, 'No se pudo completar la operación.'))
    } finally {
      const next = new Set(pendingIds.value)
      next.delete(id)
      pendingIds.value = next
    }
  }

  return {
    block,
    blockedUsers,
    error,
    hasSearched,
    isLoading: computed(() => status.value === 'pending'),
    mutationError,
    notice,
    pendingIds,
    query,
    refresh,
    results,
    search,
    searchError,
    searchedQuery,
    searching,
    unblock
  }
}
