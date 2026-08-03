from datetime import UTC, datetime
from decimal import Decimal
from typing import cast, final
from uuid import UUID, uuid4

import pytest

from modules.tickets.application.approve_ticket_request import ApproveTicketRequest
from modules.tickets.application.generate_ticket_code import GenerateTicketCode
from modules.tickets.application.list_pending_tickets import ListPendingTickets
from modules.tickets.domain.entities.ticket import (
    PendingTicketRequest,
    TicketRequest,
    TicketRequestStatus,
)
from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from modules.users.domain.entities.users import User
from shared.uow import UnitOfWork


@final
class Tickets:
    def __init__(self, ticket_request: TicketRequest) -> None:
        self.ticket_request = ticket_request
        self.price = Decimal("5.50")
        self.sequence = 0
        self.issued: list[PrintableTicket] = []

    async def find_by_id(self, _request_id: UUID, *, for_update: bool = False) -> TicketRequest:
        return self.ticket_request

    async def current_price(self) -> Decimal:
        return self.price

    async def reserve_next_ticket_sequence(self, _period: str) -> int:
        self.sequence += 1
        return self.sequence

    async def update(self, ticket_request: TicketRequest) -> None:
        self.ticket_request = ticket_request

    async def add_issued(self, _request_id: UUID, tickets: list[PrintableTicket]) -> None:
        self.issued.extend(tickets)

    async def list_pending(self) -> list[PendingTicketRequest]:
        return [
            PendingTicketRequest(
                self.ticket_request.id,
                "User",
                self.ticket_request.cantidad,
                self.ticket_request.fecha_creacion,
            )
        ]


@final
class Users:
    def __init__(self, user: User) -> None:
        self.user = user

    async def get_by_id(self, _user_id: UUID) -> User:
        return self.user


@final
class TicketsUnitOfWork:
    def __init__(self, ticket_request: TicketRequest, user: User) -> None:
        self.ticket_requests = Tickets(ticket_request)
        self.ticket_codes = self.ticket_requests
        self.users = Users(user)
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


def as_uow(value: TicketsUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, cast(object, value))


async def test_approve_pending_request_generates_codes_and_marks_it_approved() -> None:
    creator_id = uuid4()
    ticket_request = TicketRequest(2, creator_id, datetime.now(UTC))
    uow = TicketsUnitOfWork(ticket_request, User("oid", "user@example.com", "User", id=creator_id))

    approved = await ApproveTicketRequest(as_uow(uow)).approve(ticket_request.id, uuid4())

    assert approved.status == TicketRequestStatus.APPROVED
    assert approved.approved_by_id is not None and approved.approved_at is not None
    assert [ticket.codigo for ticket in uow.ticket_requests.issued] == [
        f"{approved.approved_at:%y%m}-000001",
        f"{approved.approved_at:%y%m}-000002",
    ]
    assert uow.commits == 1


@pytest.mark.parametrize("status", [TicketRequestStatus.APPROVED, TicketRequestStatus.REJECTED])
async def test_approve_rejects_non_pending_requests(status: TicketRequestStatus) -> None:
    ticket_request = TicketRequest(1, uuid4(), datetime.now(UTC), status=status)
    uow = TicketsUnitOfWork(ticket_request, User("oid", "user@example.com", "User"))

    with pytest.raises(ValueError, match="ya ha sido aprobada"):
        await ApproveTicketRequest(as_uow(uow)).approve(ticket_request.id, uuid4())

    assert not uow.ticket_requests.issued and uow.commits == 0


async def test_ticket_code_is_monthly_and_zero_padded() -> None:
    class Codes:
        def __init__(self) -> None:
            self.sequence = 0

        async def reserve_next_ticket_sequence(self, period: str) -> int:
            self.sequence += 1
            return self.sequence

    generator = GenerateTicketCode(Codes())
    assert await generator.generate(datetime(2026, 7, 1)) == "2607-000001"
    assert await generator.generate(datetime(2026, 7, 1)) == "2607-000002"


async def test_list_pending_returns_creator_pending_requests() -> None:
    creator_id = uuid4()
    ticket_request = TicketRequest(1, creator_id, datetime.now(UTC))
    uow = TicketsUnitOfWork(ticket_request, User("oid", "user@example.com", "User"))

    assert await ListPendingTickets(as_uow(uow)).list() == [
        PendingTicketRequest(ticket_request.id, "User", 1, ticket_request.fecha_creacion)
    ]
