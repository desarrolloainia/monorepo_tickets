import type { BlockedUserDTO, MicrosoftUserDTO } from '@/shared/api'

type ApiOptions = {
  baseURL: string
  headers?: HeadersInit
}

export function fetchBlockedUsers(options: ApiOptions) {
  return $fetch<BlockedUserDTO[]>('/users/blocked', {
    ...options,
    credentials: 'include'
  })
}

export function searchMicrosoftUsers(query: string, options: ApiOptions) {
  return $fetch<MicrosoftUserDTO[]>('/users/microsoft/search', {
    ...options,
    credentials: 'include',
    query: { q: query }
  })
}

export function blockMicrosoftUser(microsoftOid: string, options: ApiOptions) {
  return $fetch<BlockedUserDTO>(`/users/blocked/${encodeURIComponent(microsoftOid)}`, {
    ...options,
    method: 'PUT',
    credentials: 'include'
  })
}

export function unblockMicrosoftUser(microsoftOid: string, options: ApiOptions) {
  return $fetch(`/users/blocked/${encodeURIComponent(microsoftOid)}`, {
    ...options,
    method: 'DELETE',
    credentials: 'include'
  })
}
