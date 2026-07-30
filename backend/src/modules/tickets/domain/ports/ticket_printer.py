from typing import Protocol

from modules.tickets.domain.entities.ticket import Ticket


class TicketPrinter(Protocol):
    async def print_ticket(self, ticket: Ticket) -> None:
        ...
