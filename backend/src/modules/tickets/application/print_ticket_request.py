from uuid import UUID

from fastapi import Request
from fastapi.responses import HTMLResponse

from modules.tickets.domain.entities.ticket import TicketRequestStatus
from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from modules.tickets.domain.ports.ticket_printer import TicketPrinter
from modules.users.domain.entities.users import User, UserRole
from shared.uow import UnitOfWork


class PrintTicketRequest:
    def __init__(self, unit_of_work: UnitOfWork, printer: TicketPrinter) -> None:
        self.uow = unit_of_work
        self.printer = printer

    async def render(self, request: Request, request_id: UUID, requester: User) -> HTMLResponse:
        ticket_request = await self.uow.ticket_requests.find_by_id(request_id)
        if ticket_request is None or (
            ticket_request.created_by_id != requester.id and requester.role != UserRole.APPROVER
        ):
            raise ValueError("Solicitud no encontrada")
        if ticket_request.status != TicketRequestStatus.APPROVED:
            raise ValueError("La solicitud no ha sido aprobada")
        creator = await self.uow.users.get_by_id(ticket_request.created_by_id)
        if creator is None:
            raise ValueError("Usuario no encontrado")
        tickets = [
            PrintableTicket(
                creator.name, ticket.codigo, ticket.fecha_emision, ticket.precio_unitario
            )
            for ticket in await self.uow.ticket_requests.list_issued(request_id)
        ]
        return self.printer.render(
            request, tickets, creator.name, requester.role == UserRole.APPROVER
        )
