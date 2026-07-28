from __future__ import annotations

from datetime import datetime
from typing import ClassVar, final
from uuid import uuid4

import pytest

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.infrastructure.escpos import ticket_printer


@final
class Printer:
    instances: ClassVar[list[Printer]] = []

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.output: list[str] = []
        self.cut_called = False
        self.closed = False
        self.instances.append(self)

    def text(self, value: str) -> None:
        self.output.append(value)

    def qr(self, value: str) -> None:
        self.output.append(value)

    def cut(self) -> None:
        self.cut_called = True

    def close(self) -> None:
        self.closed = True


async def test_escpos_printer_prints_ticket(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ticket_printer, "Network", Printer)
    now = datetime.now().astimezone()
    ticket = Ticket(
        title="Entrada",
        nombre="Ana",
        description="Concierto",
        status="nuevo",
        codigo="ABC",
        codigo_qr="qr:ABC",
        fecha_emision=now,
        fecha_creacion=now,
        cantidad=1,
        aprobacion=True,
        id=uuid4(),
    )

    await ticket_printer.EscposNetworkTicketPrinter("192.168.1.100").print_ticket(ticket)

    printer = Printer.instances[-1]
    assert printer.host == "192.168.1.100" and printer.port == 9100
    assert printer.output[-1] == "qr:ABC"
    assert printer.cut_called and printer.closed
