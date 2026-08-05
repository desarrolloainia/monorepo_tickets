import type {
    SpendingSummaryDTO,
    TicketPriceConfigurationDTO,
    TicketPriceOverviewDTO,
  UserSpendingDetailDTO,
  UserSpendingDTO
} from '@/shared/api'

export type UserSpending = UserSpendingDTO

type ApiOptions = {
  baseURL: string
  headers?: HeadersInit
}

export function fetchSpending(period: string, options: ApiOptions) {
  return $fetch<SpendingSummaryDTO>('/tickets/spending', {
    ...options,
    credentials: 'include',
    query: { period }
  })
}

export function fetchUserSpending(userId: string, period: string, options: ApiOptions) {
  return $fetch<UserSpendingDetailDTO>(`/tickets/spending/users/${userId}`, {
    ...options,
    credentials: 'include',
    query: { period }
  })
}

export function fetchTicketPrice(options: ApiOptions) {
  return $fetch<TicketPriceOverviewDTO>('/tickets/price-configurations', {
    ...options,
    credentials: 'include'
  })
}

export function updateTicketPrice(
  precioUnitario: string,
  expectedConfigurationId: string | null,
  options: ApiOptions
) {
  return $fetch<TicketPriceConfigurationDTO>('/tickets/price-configurations', {
    ...options,
    method: 'POST',
    credentials: 'include',
    body: {
      precio_unitario: precioUnitario,
      expected_configuration_id: expectedConfigurationId
    }
  })
}
