from datetime import datetime
from typing import cast, final
from uuid import UUID, uuid4

import pytest

from modules.tickets.api.dtos import TicketCreateDTO
from modules.tickets.application.approve_ticket import ApproveTicket
from modules.tickets.application.create_ticket import CreateTicket
from modules.tickets.application.delete_ticket import DeleteTicket
from modules.tickets.application.get_ticket_by_id import GetTicketById
from modules.tickets.application.list_tickets import ListTickets
from modules.tickets.domain.entities.ticket import Ticket
from shared.uow import UnitOfWork


def ticket() -> Ticket:
    now = datetime.now().astimezone()
    return Ticket(
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


@final
class Tickets:
    def __init__(self, current: Ticket | None):
        self.current = current
        self.deleted: UUID | None = None

    async def add(self, value: Ticket) -> Ticket:
        self.current = value
        return value

    async def remove(self, ticket_id: UUID) -> None:
        self.deleted = ticket_id

    async def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.current if self.current and self.current.id == ticket_id else None

    async def list_all(self) -> list[Ticket]:
        return [] if self.current is None else [self.current]


@final
class TicketsUnitOfWork:
    def __init__(self, tickets: Tickets):
        self.tickets = tickets
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


@final
class Printer:
    def __init__(self):
        self.printed: list[Ticket] = []

    async def print_ticket(self, ticket: Ticket) -> None:
        self.printed.append(ticket)


def as_uow(value: TicketsUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, cast(object, value))


async def test_ticket_use_cases_read_and_write_tickets():
    current = ticket()
    uow = TicketsUnitOfWork(Tickets(current))
    printer = Printer()

    assert await ListTickets(as_uow(uow)).list() == [current]
    assert await GetTicketById(as_uow(uow)).get_by_id(current.id) is current

    await DeleteTicket(as_uow(uow)).delete(current.id)
    approved = await ApproveTicket(as_uow(uow), printer).approve(current.id)

    assert uow.tickets.deleted == current.id
    assert approved.aprobacion and uow.commits == 2
    assert printer.printed == [approved]


async def test_create_ticket_assigns_server_values_and_commits():
    uow = TicketsUnitOfWork(Tickets(None))

    created = await CreateTicket(as_uow(uow)).create(
        TicketCreateDTO(title="Entrada", description="Concierto", cantidad=1)
    )

    assert created.nombre == created.title
    assert created.codigo == created.codigo_qr
    assert not created.aprobacion and uow.commits == 1


async def test_get_and_approve_raise_for_unknown_ticket():
    uow = TicketsUnitOfWork(Tickets(None))
    ticket_id = uuid4()
    printer = Printer()

    with pytest.raises(ValueError, match="Ticket no encontrado"):
        _ = await GetTicketById(as_uow(uow)).get_by_id(ticket_id)
    with pytest.raises(ValueError, match="Ticket no encontrado"):
        _ = await ApproveTicket(as_uow(uow), printer).approve(ticket_id)

    assert uow.commits == 0
    assert not printer.printed
