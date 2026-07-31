from collections.abc import Sequence
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from modules.tickets.domain.entities.ticket import TicketRequest
from modules.tickets.domain.entities.ticket_printer import PrintableTicket


class TicketRequestRepository(Protocol):
    async def add(self, request: TicketRequest) -> TicketRequest: ...

    async def find_by_id(
        self, request_id: UUID, *, for_update: bool = False
    ) -> TicketRequest | None: ...

    async def list_by_creator(self, creator_id: UUID) -> Sequence[TicketRequest]: ...

    async def update(self, request: TicketRequest) -> None: ...

    async def current_price(self) -> Decimal | None: ...

    async def add_issued(self, request_id: UUID, tickets: Sequence[PrintableTicket]) -> None: ...

    async def list_issued(self, request_id: UUID) -> Sequence[PrintableTicket]: ...


class TicketCodeRepository(Protocol):
    async def reserve_next_ticket_sequence(self, period: str) -> int: ...
