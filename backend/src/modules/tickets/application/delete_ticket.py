from uuid import UUID

from shared import uow


class DeleteTicket:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def delete(self, ticket_id: UUID, created_by_id: UUID) -> None:
        if await self.uow.tickets.find_by_id(ticket_id, created_by_id) is None:
            raise ValueError("Ticket no encontrado")
        await self.uow.tickets.remove(ticket_id, created_by_id)
        await self.uow.commit()
