from typing import Protocol
from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.domain.ports.generate_qr import QrGenerator


class TicketFinder(Protocol):
    async def find_by_id(self, ticket_id: UUID) -> Ticket | None: ...


class TicketQrUseCase:
    def __init__(self, repository: TicketFinder, qr_generator: QrGenerator):
        self.repository = repository
        self.qr_generator = qr_generator

    async def generar_qr(self, ticket_id: UUID) -> Ticket:
        ticket = await self.repository.find_by_id(ticket_id)
        if ticket is None:
            raise ValueError("Ticket no encontrado")

        ticket.codigo_qr = await self.qr_generator.generate_qr(ticket)
        return ticket
