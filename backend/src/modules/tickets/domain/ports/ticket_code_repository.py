from typing import Protocol


class TicketCodeRepository(Protocol):
    async def reserve_next_ticket_sequence(self, period: str) -> int: ...
