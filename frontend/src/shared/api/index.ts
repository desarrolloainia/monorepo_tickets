export type { $defs, components, operations, paths, webhooks } from './openapi'

import type { components } from './openapi'

export type UserDTO = components['schemas']['UserDTO']
export type PendingTicketRequestDTO = components['schemas']['PendingTicketRequestDTO']
export type TicketRequestDTO = components['schemas']['TicketRequestDTO']
export type TicketRequestCreateDTO = components['schemas']['TicketRequestCreateDTO']
export type TicketRequestStatus = components['schemas']['TicketRequestStatus']
export type SpendingRequestDTO = components['schemas']['SpendingRequestDTO']
export type SpendingSummaryDTO = components['schemas']['SpendingSummaryDTO']
export type UserSpendingDTO = components['schemas']['UserSpendingDTO']
export type UserSpendingDetailDTO = components['schemas']['UserSpendingDetailDTO']
export type BlockedUserDTO = components['schemas']['BlockedUserDTO']
export type MicrosoftUserDTO = components['schemas']['MicrosoftUserDTO']
export type TicketPriceConfigurationDTO = components['schemas']['TicketPriceConfigurationDTO']
export type TicketPriceOverviewDTO = components['schemas']['TicketPriceOverviewDTO']
