from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from modules.tickets.domain.entities.ticket import Ticket


class TicketRepository(Protocol):
    async def add(self, ticket: Ticket) -> Ticket: ...

    async def remove(self, ticket_id: UUID, created_by_id: UUID | None = None) -> None: ...

    async def find_by_id(
        self, ticket_id: UUID, created_by_id: UUID | None = None
    ) -> Ticket | None: ...

    async def list_all(self, created_by_id: UUID | None = None) -> Sequence[Ticket]: ...
