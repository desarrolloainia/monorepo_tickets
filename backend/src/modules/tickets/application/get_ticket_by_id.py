from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket
from shared import uow


class GetTicketById:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def get_by_id(self, ticket_id: UUID, created_by_id: UUID) -> Ticket:
        ticket = await self.uow.tickets.find_by_id(ticket_id, created_by_id)
        if ticket is None:
            raise ValueError("Ticket no encontrado")
        return ticket
