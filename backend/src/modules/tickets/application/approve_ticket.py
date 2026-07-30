from datetime import UTC, datetime
from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.domain.ports.ticket_printer import TicketPrinter
from shared import uow


class ApproveTicket:
    def __init__(self, unit_of_work: uow.UnitOfWork, printer: TicketPrinter) -> None:
        self.uow: uow.UnitOfWork = unit_of_work
        self.printer: TicketPrinter = printer

    async def approve(self, ticket_id: UUID, approved_by_id: UUID) -> Ticket:
        ticket = await self.uow.tickets.find_by_id(ticket_id)
        if ticket is None:
            raise ValueError("Ticket no encontrado")

        ticket.aprobacion = True
        ticket.approved_by_id = approved_by_id
        ticket.approved_at = datetime.now(UTC)
        ticket = await self.uow.tickets.add(ticket)
        await self.uow.commit()
        await self.printer.print_ticket(ticket)
        return ticket
