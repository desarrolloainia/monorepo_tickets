from typing import Protocol

from modules.tickets.domain.entities.ticket import Ticket


class QrGenerator(Protocol):
    async def generate_qr(self, ticket: Ticket) -> str: ...
