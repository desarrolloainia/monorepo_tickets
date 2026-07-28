from typing import Protocol
from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.domain.ports.ticket_printer import TicketPrinter


class TicketFinder(Protocol):
    async def find_by_id(self, ticket_id: UUID) -> Ticket | None: ...


class TicketPrinterUseCase:
    def __init__(self, printer: TicketPrinter, repository: TicketFinder):
        self.printer = printer
        self.repository = repository

    async def imprimir_ticket(self, ticket_id: UUID) -> None:
        ticket = await self.repository.find_by_id(ticket_id)
        if ticket is None:
            raise ValueError("Ticket no encontrado")

        await self.printer.print_ticket(ticket)
