from uuid import UUID

from shared import uow


class DeleteTicket:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def delete(self, ticket_id: UUID) -> None:
        await self.uow.tickets.remove(ticket_id)
        await self.uow.commit()
