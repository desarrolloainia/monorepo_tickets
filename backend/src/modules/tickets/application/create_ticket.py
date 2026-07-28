from datetime import UTC, datetime
from uuid import uuid4

from modules.tickets.api.dtos import TicketCreateDTO
from modules.tickets.domain.entities.ticket import Ticket
from shared import uow


class CreateTicket:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def create(self, datos_ticket: TicketCreateDTO) -> Ticket:
        now = datetime.now(UTC)
        # ponytail: UUID is the ticket code until the sequence and QR adapters use the shared UoW.
        codigo = uuid4().hex
        ticket = Ticket(
            title=datos_ticket.title,
            nombre=datos_ticket.title,
            description=datos_ticket.description,
            status="nuevo",
            codigo=codigo,
            codigo_qr=codigo,
            fecha_emision=now,
            fecha_creacion=now,
            cantidad=datos_ticket.cantidad,
            aprobacion=False,
        )
        ticket = await self.uow.tickets.add(ticket)
        await self.uow.commit()
        return ticket
