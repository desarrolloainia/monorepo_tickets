from datetime import UTC, datetime
from uuid import UUID

from modules.tickets.domain.entities.ticket import TicketRequest
from shared.uow import UnitOfWork


class CreateTicketRequest:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def create(self, cantidad: int, created_by_id: UUID) -> TicketRequest:
        request = TicketRequest(cantidad, created_by_id, datetime.now(UTC))
        await self.uow.ticket_requests.add(request)
        await self.uow.commit()
        return request
