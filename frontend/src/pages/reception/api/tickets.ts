import type { PendingTicketRequestDTO, TicketRequestDTO } from '@/shared/api'

type TicketApiOptions = {
  baseURL: string
  headers?: HeadersInit
}

export function fetchPendingTicketRequests(options: TicketApiOptions) {
  return $fetch<PendingTicketRequestDTO[]>('/tickets/pending', {
    ...options,
    credentials: 'include'
  })
}

export function approveTicketRequest(baseURL: string, id: string) {
  return $fetch<TicketRequestDTO>(`/tickets/${id}/approve`, {
    baseURL,
    method: 'POST',
    credentials: 'include'
  })
}
