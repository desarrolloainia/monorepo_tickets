from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from modules.tickets.domain.entities.ticket import (
    PendingTicketRequest,
    SpendingRequest,
    TicketRequest,
    UserSpending,
)
from modules.tickets.domain.entities.ticket_price import TicketPriceConfiguration
from modules.tickets.domain.entities.ticket_printer import PrintableTicket


class TicketRequestRepository(Protocol):
    async def add(self, request: TicketRequest) -> TicketRequest: ...

    async def find_by_id(
        self, request_id: UUID, *, for_update: bool = False
    ) -> TicketRequest | None: ...

    async def list_by_creator(self, creator_id: UUID) -> Sequence[TicketRequest]: ...

    async def update(self, request: TicketRequest) -> None: ...

    async def current_price(self) -> Decimal | None: ...

    async def current_price_configuration(
        self, *, for_update: bool = False
    ) -> TicketPriceConfiguration | None: ...

    async def list_price_configurations(
        self, limit: int = 10
    ) -> list[TicketPriceConfiguration]: ...

    async def add_price_configuration(
        self, configuration: TicketPriceConfiguration
    ) -> TicketPriceConfiguration: ...

    async def add_issued(self, request_id: UUID, tickets: Sequence[PrintableTicket]) -> None: ...

    async def list_issued(self, request_id: UUID) -> Sequence[PrintableTicket]: ...

    async def list_pending(self) -> list[PendingTicketRequest]: ...

    async def spending_by_user(self, start: datetime, end: datetime) -> list[UserSpending]: ...

    async def spending_requests(
        self, user_id: UUID, start: datetime, end: datetime
    ) -> list[SpendingRequest]: ...


class TicketCodeRepository(Protocol):
    async def reserve_next_ticket_sequence(self, period: str) -> int: ...
