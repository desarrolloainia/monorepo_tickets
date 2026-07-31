from collections.abc import Sequence
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from modules.tickets.domain.entities.ticket_printer import PrintableTicket


class HtmlTicketPrinter:
    def __init__(self) -> None:
        template_dir = Path(__file__).parent.parent / "template"
        self.templates = Jinja2Templates(directory=template_dir)

    def render(
        self, request: Request, tickets: Sequence[PrintableTicket], nombre: str
    ) -> HTMLResponse:
        # ponytail: the template reserves the twelfth cell for the signature.
        groups = [tickets[index : index + 11] for index in range(0, len(tickets), 11)]
        return self.templates.TemplateResponse(
            request=request,
            name="tickets.html",
            context={"grupos_tickets": groups, "nombre": nombre},
        )
