from modules.tickets.domain.entities.ticket import PendingTicketRequest
from shared.uow import UnitOfWork


class ListPendingTickets:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def list(self) -> list[PendingTicketRequest]:
        return await self.uow.ticket_requests.list_pending()
