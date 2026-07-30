from datetime import datetime
from uuid import uuid4

import pytest

from modules.tickets.application.ticket_printer_use_case import TicketPrinterUseCase
from modules.tickets.domain.entities.ticket import Ticket


class Repository:
    def __init__(self, ticket: Ticket | None):
        self.ticket = ticket

    async def find_by_id(self, ticket_id):
        return self.ticket


class Printer:
    def __init__(self):
        self.printed: list[Ticket] = []

    async def print_ticket(self, ticket: Ticket) -> None:
        self.printed.append(ticket)


def ticket() -> Ticket:
    now = datetime.now().astimezone()
    return Ticket(
        id=uuid4(),
        title="Entrada",
        nombre="Ana",
        description="Concierto",
        status="nuevo",
        codigo="2607-000001",
        codigo_qr="",
        fecha_emision=now,
        fecha_creacion=now,
        cantidad=1,
        aprobacion=False,
    )


async def test_imprimir_ticket_envia_el_ticket_al_dispositivo():
    current_ticket = ticket()
    printer = Printer()

    await TicketPrinterUseCase(printer, Repository(current_ticket)).imprimir_ticket(
        current_ticket.id
    )

    assert printer.printed == [current_ticket]


async def test_imprimir_ticket_falla_si_el_ticket_no_existe():
    with pytest.raises(ValueError, match="Ticket no encontrado"):
        await TicketPrinterUseCase(Printer(), Repository(None)).imprimir_ticket(uuid4())
