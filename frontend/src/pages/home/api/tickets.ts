import type { TicketRequestCreateDTO, TicketRequestDTO } from '@/shared/api'

export type TicketAmount = TicketRequestCreateDTO['cantidad']

type TicketApiOptions = {
  baseURL: string
  headers?: HeadersInit
}

export function fetchTicketRequests(options: TicketApiOptions) {
  return $fetch<TicketRequestDTO[]>('/tickets/', {
    ...options,
    credentials: 'include'
  })
}

export function createTicketRequest(baseURL: string, cantidad: TicketAmount) {
  return $fetch<TicketRequestDTO>('/tickets/', {
    baseURL,
    method: 'POST',
    credentials: 'include',
    body: { cantidad } satisfies TicketRequestCreateDTO
  })
}
