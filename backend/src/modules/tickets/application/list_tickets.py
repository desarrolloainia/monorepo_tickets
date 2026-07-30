from collections.abc import Sequence
from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket
from shared import uow


class ListTickets:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def list(self, created_by_id: UUID) -> Sequence[Ticket]:
        return await self.uow.tickets.list_all(created_by_id)
