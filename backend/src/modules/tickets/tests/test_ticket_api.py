from datetime import UTC, datetime
from decimal import Decimal
from typing import cast
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from modules.auth.dependencies import current_user, get_uow
from modules.tickets.api.api import router
from modules.tickets.api.dtos import TicketRequestCreateDTO
from modules.tickets.domain.entities.ticket import (
    SpendingRequest,
    TicketRequest,
    TicketRequestStatus,
    UserSpending,
)
from modules.tickets.domain.entities.ticket_price import TicketPriceConfiguration
from modules.users.domain.entities.users import User, UserRole
from shared.uow import UnitOfWork


class SpendingTickets:
    def __init__(self) -> None:
        self.users: list[UserSpending] = []
        self.requests: list[SpendingRequest] = []
        self.range: tuple[datetime, datetime] | None = None
        self.configurations: list[TicketPriceConfiguration] = []

    async def spending_by_user(self, start: datetime, end: datetime) -> list[UserSpending]:
        self.range = (start, end)
        return self.users

    async def spending_requests(
        self, _user_id: UUID, start: datetime, end: datetime
    ) -> list[SpendingRequest]:
        self.range = (start, end)
        return self.requests

    async def current_price_configuration(
        self, *, for_update: bool = False
    ) -> TicketPriceConfiguration | None:
        del for_update
        return self.configurations[0] if self.configurations else None

    async def list_price_configurations(self, limit: int = 10) -> list[TicketPriceConfiguration]:
        return self.configurations[:limit]

    async def add_price_configuration(
        self, configuration: TicketPriceConfiguration
    ) -> TicketPriceConfiguration:
        self.configurations.insert(0, configuration)
        return configuration


class SpendingUsers:
    def __init__(self, user: User | None) -> None:
        self.user = user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.user if self.user and self.user.id == user_id else None


class SpendingUow:
    def __init__(self, user: User | None = None) -> None:
        self.ticket_requests = SpendingTickets()
        self.users = SpendingUsers(user)
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


class NotificationUsers:
    def __init__(self, users: list[User]) -> None:
        self.users = users

    async def list_all(self) -> list[User]:
        return self.users

    async def get_by_id(self, user_id: UUID) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)


class NotificationUow:
    def __init__(self, users: list[User]) -> None:
        self.users = NotificationUsers(users)


def spending_client(
    uow: object,
    role: UserRole = UserRole.RRHH,
    user: User | None = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_uow] = lambda: cast(UnitOfWork, uow)
    authenticated_user = user or User("requester", "requester@example.com", "Requester", role)
    app.dependency_overrides[current_user] = lambda: authenticated_user
    return TestClient(app)


def test_ticket_router_has_approval_but_no_edit_route() -> None:
    routes = {
        (route.path, method)
        for route in router.routes
        if isinstance(route, APIRoute)
        for method in route.methods or set()
    }

    assert ("/tickets/{ticket_request_id}/approve", "POST") in routes
    assert ("/tickets/{ticket_request_id}", "PATCH") not in routes
    assert ("/tickets/{ticket_request_id}", "PUT") not in routes
    assert ("/tickets/pending", "GET") in routes
    assert ("/tickets/pending/{ticket_request_id}", "GET") in routes
    assert ("/tickets/{ticket_request_id}/approve", "POST") in routes

    paths = [route.path for route in router.routes if isinstance(route, APIRoute)]
    assert paths.index("/tickets/spending") < paths.index("/tickets/{ticket_request_id}")
    assert paths.index("/tickets/spending/users/{user_id}") < paths.index(
        "/tickets/{ticket_request_id}"
    )


def test_ticket_request_only_accepts_supported_quantities() -> None:
    assert TicketRequestCreateDTO(cantidad=11).cantidad == 11
    assert TicketRequestCreateDTO(cantidad=22).cantidad == 22

    with pytest.raises(ValidationError):
        TicketRequestCreateDTO.model_validate({"cantidad": 12})


def test_spending_summary_uses_month_range_and_includes_zero_users() -> None:
    uow = SpendingUow()
    uow.ticket_requests.users = [
        UserSpending(uuid4(), "Ana", "ana@example.com", Decimal("11.00"), 2),
        UserSpending(uuid4(), "Luis", "luis@example.com", Decimal("0.00"), 0),
    ]

    response = spending_client(uow).get("/tickets/spending?period=2026-07")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "period": "2026-07",
        "total_gastado": "11.00",
        "tickets_emitidos": 2,
        "gasto_medio_por_usuario": "5.50",
        "usuarios": [
            {
                "user_id": str(uow.ticket_requests.users[0].user_id),
                "nombre": "Ana",
                "email": "ana@example.com",
                "total_gastado": "11.00",
                "tickets_emitidos": 2,
            },
            {
                "user_id": str(uow.ticket_requests.users[1].user_id),
                "nombre": "Luis",
                "email": "luis@example.com",
                "total_gastado": "0.00",
                "tickets_emitidos": 0,
            },
        ],
    }
    assert uow.ticket_requests.range == (
        datetime(2026, 7, 1, tzinfo=UTC),
        datetime(2026, 8, 1, tzinfo=UTC),
    )


def test_spending_rejects_invalid_period_and_non_rrhh() -> None:
    assert spending_client(SpendingUow()).get("/tickets/spending?period=2026-13").status_code == 422
    assert (
        spending_client(SpendingUow(), UserRole.APPROVER).get("/tickets/spending").status_code
        == status.HTTP_403_FORBIDDEN
    )


def test_accountant_can_read_spending() -> None:
    response = spending_client(SpendingUow(), UserRole.ACCOUNTANT).get("/tickets/spending")
    assert response.status_code == status.HTTP_200_OK


def test_accountant_reads_default_price_and_appends_a_new_configuration() -> None:
    accountant = User(
        "accountant", "accountant@example.com", "Ana Contable", UserRole.ACCOUNTANT
    )
    uow = SpendingUow()
    client = spending_client(uow, UserRole.ACCOUNTANT, accountant)

    initial = client.get("/tickets/price-configurations")
    created = client.post(
        "/tickets/price-configurations",
        json={"precio_unitario": "6.25", "expected_configuration_id": None},
    )
    history = client.get("/tickets/price-configurations")

    assert initial.status_code == status.HTTP_200_OK
    assert initial.json() == {
        "precio_unitario": "5.50",
        "current_configuration_id": None,
        "historial": [],
    }
    assert created.status_code == status.HTTP_201_CREATED
    assert created.json()["precio_unitario"] == "6.25"
    assert created.json()["updated_by_name"] == "Ana Contable"
    assert history.json()["precio_unitario"] == "6.25"
    assert len(history.json()["historial"]) == 1
    assert uow.commits == 1


@pytest.mark.parametrize("price", ["0", "-1", "1.234", "999999999.99"])
def test_price_update_rejects_invalid_money(price: str) -> None:
    response = spending_client(SpendingUow(), UserRole.ACCOUNTANT).post(
        "/tickets/price-configurations",
        json={"precio_unitario": price, "expected_configuration_id": None},
    )
    assert response.status_code == 422


def test_price_update_rejects_stale_configuration_and_non_accountants() -> None:
    current = TicketPriceConfiguration(
        Decimal("5.75"),
        uuid4(),
        datetime.now(UTC),
        "Previous Accountant",
    )
    uow = SpendingUow()
    uow.ticket_requests.configurations = [current]

    stale = spending_client(uow, UserRole.ACCOUNTANT).post(
        "/tickets/price-configurations",
        json={"precio_unitario": "6.00", "expected_configuration_id": str(uuid4())},
    )
    forbidden = spending_client(uow, UserRole.RRHH).post(
        "/tickets/price-configurations",
        json={"precio_unitario": "6.00", "expected_configuration_id": str(current.id)},
    )

    assert stale.status_code == status.HTTP_409_CONFLICT
    assert forbidden.status_code == status.HTTP_403_FORBIDDEN
    assert len(uow.ticket_requests.configurations) == 1


def test_user_spending_returns_annual_approved_request_details() -> None:
    user = User("user", "user@example.com", "User")
    request_id = uuid4()
    uow = SpendingUow(user)
    uow.ticket_requests.requests = [
        SpendingRequest(
            request_id,
            datetime(2026, 3, 4, 10, tzinfo=UTC),
            2,
            Decimal("11.00"),
        )
    ]

    response = spending_client(uow).get(f"/tickets/spending/users/{user.id}?period=2026")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["solicitudes"] == [
        {
            "id": str(request_id),
            "fecha_emision": "2026-03-04T10:00:00Z",
            "tickets_emitidos": 2,
            "total_gastado": "11.00",
        }
    ]
    assert response.json()["total_gastado"] == "11.00"
    assert uow.ticket_requests.range == (
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2027, 1, 1, tzinfo=UTC),
    )


def test_user_spending_returns_404_for_unknown_user() -> None:
    response = spending_client(SpendingUow()).get(f"/tickets/spending/users/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("requester_role", [UserRole.USER, UserRole.ACCOUNTANT])
def test_creation_notifies_only_approvers(
    monkeypatch: pytest.MonkeyPatch, requester_role: UserRole
) -> None:
    requester = User("requester", "requester@example.com", "Requester", requester_role)
    approvers = [
        User("approver-1", "one@example.com", "One", UserRole.APPROVER),
        User("approver-2", "two@example.com", "Two", UserRole.APPROVER),
    ]
    rrhh = User("rrhh", "rrhh@example.com", "RRHH", UserRole.RRHH)
    uow = NotificationUow([*approvers, requester, rrhh])
    sent_to: list[str] = []

    async def create(_self: object, cantidad: int, created_by_id: UUID) -> TicketRequest:
        return TicketRequest(cantidad, created_by_id, datetime.now(UTC))

    def send(recipients: list[str], *_args: object) -> None:
        sent_to.extend(recipients)

    monkeypatch.setattr("modules.tickets.api.api.CreateTicketRequest.create", create)
    monkeypatch.setattr("modules.tickets.api.api.send_reception_emails", send)
    client = spending_client(uow, user=requester)

    response = client.post("/tickets/", json={"cantidad": 11})

    assert response.status_code == status.HTTP_201_CREATED
    assert sent_to == [approver.email for approver in approvers]


def test_approval_notifies_the_requester(monkeypatch: pytest.MonkeyPatch) -> None:
    requester = User("requester", "requester@example.com", "Requester")
    approver = User("approver", "approver@example.com", "Approver", UserRole.APPROVER)
    uow = NotificationUow([requester, approver])
    ticket_request = TicketRequest(
        22,
        requester.id,
        datetime.now(UTC),
        status=TicketRequestStatus.APPROVED,
        approved_by_id=approver.id,
        approved_at=datetime.now(UTC),
    )
    sent_to: list[str] = []

    async def approve(_self: object, _request_id: UUID, _approver_id: UUID) -> TicketRequest:
        return ticket_request

    def send(recipient: str, *_args: object) -> None:
        sent_to.append(recipient)

    monkeypatch.setattr("modules.tickets.api.api.ApproveTicketRequest.approve", approve)
    monkeypatch.setattr("modules.tickets.api.api.send_approval_email", send)
    client = spending_client(uow, UserRole.APPROVER, approver)

    response = client.post(f"/tickets/{ticket_request.id}/approve")

    assert response.status_code == status.HTTP_200_OK
    assert sent_to == [requester.email]
