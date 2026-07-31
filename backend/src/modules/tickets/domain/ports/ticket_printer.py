from collections.abc import Sequence
from typing import Protocol

from fastapi import Request
from fastapi.responses import HTMLResponse

from modules.tickets.domain.entities.ticket_printer import PrintableTicket


class TicketPrinter(Protocol):
    def render(
        self, request: Request, tickets: Sequence[PrintableTicket], nombre: str
    ) -> HTMLResponse: ...
