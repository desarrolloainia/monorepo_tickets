export type { $defs, components, operations, paths, webhooks } from './openapi'

import type { components } from './openapi'

export type UserDTO = components['schemas']['UserDTO']
export type PendingTicketRequestDTO = components['schemas']['PendingTicketRequestDTO']
export type TicketRequestDTO = components['schemas']['TicketRequestDTO']
export type TicketRequestCreateDTO = components['schemas']['TicketRequestCreateDTO']
export type TicketRequestStatus = components['schemas']['TicketRequestStatus']
