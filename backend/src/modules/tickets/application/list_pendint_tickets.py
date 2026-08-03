from uuid import UUID

from modules.tickets.domain.ports.ticket_request_repository import TicketCodeRepository
from shared.uow import UnitOfWork


class PendingTicketRequestRepository(TicketCodeRepository):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work


async def get(self, request_id: UUID) -> TicketRequest:
