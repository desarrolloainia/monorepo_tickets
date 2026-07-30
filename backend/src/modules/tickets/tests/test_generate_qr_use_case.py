from datetime import datetime
from uuid import uuid4

import pytest

from modules.tickets.application.generate_qr_use_case import TicketQrUseCase
from modules.tickets.domain.entities.ticket import Ticket


class Repository:
    def __init__(self, ticket: Ticket | None):
        self.ticket = ticket

    async def find_by_id(self, ticket_id):
        return self.ticket


class Generator:
    async def generate_qr(self, ticket: Ticket) -> str:
        return f"qr:{ticket.codigo}"


def ticket() -> Ticket:
    now = datetime.now().astimezone()
    return Ticket(
        id=uuid4(),
        title="Entrada",
        nombre="Ana",
        description="Concierto",
        status="nuevo",
        codigo="ABC",
        codigo_qr="",
        fecha_emision=now,
        fecha_creacion=now,
        cantidad=1,
        aprobacion=False,
    )


async def test_generar_qr_asigna_el_codigo_generado():
    result = await TicketQrUseCase(Repository(ticket()), Generator()).generar_qr(uuid4())

    assert result.codigo_qr == "qr:ABC"


async def test_generar_qr_falla_si_no_existe_el_ticket():
    with pytest.raises(ValueError, match="Ticket no encontrado"):
        await TicketQrUseCase(Repository(None), Generator()).generar_qr(uuid4())
