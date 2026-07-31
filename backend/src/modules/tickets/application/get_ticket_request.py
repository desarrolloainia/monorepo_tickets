from uuid import UUID

from modules.tickets.domain.entities.ticket import TicketRequest
from shared.uow import UnitOfWork


class GetTicketRequest:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def get(self, request_id: UUID, requester_id: UUID) -> TicketRequest:
        request = await self.uow.ticket_requests.find_by_id(request_id)
        if request is None or request.created_by_id != requester_id:
            raise ValueError("Solicitud no encontrada")
        return request
