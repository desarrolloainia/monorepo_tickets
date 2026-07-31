from datetime import UTC, datetime
from uuid import UUID

from modules.tickets.application.generate_ticket_code import GenerateTicketCode
from modules.tickets.domain.entities.ticket import TicketRequest, TicketRequestStatus
from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from shared.uow import UnitOfWork


class ApproveTicketRequest:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def approve(self, request_id: UUID, approved_by_id: UUID) -> TicketRequest:
        request = await self.uow.ticket_requests.find_by_id(request_id, for_update=True)
        if request is None:
            raise ValueError("Solicitud no encontrada")
        if request.status != TicketRequestStatus.PENDING:
            raise ValueError("La solicitud ya ha sido aprobada")

        price = await self.uow.ticket_requests.current_price()
        if price is None:
            raise ValueError("No hay precio de ticket configurado")
        issued_at = datetime.now(UTC)
        generator = GenerateTicketCode(self.uow.ticket_codes)
        tickets = [
            PrintableTicket("", await generator.generate(issued_at), issued_at, price)
            for _ in range(request.cantidad)
        ]
        request.status = TicketRequestStatus.APPROVED
        request.approved_by_id = approved_by_id
        request.approved_at = issued_at
        await self.uow.ticket_requests.update(request)
        await self.uow.ticket_requests.add_issued(request.id, tickets)
        await self.uow.commit()
        return request
