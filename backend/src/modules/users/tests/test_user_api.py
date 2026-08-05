from typing import cast

from fastapi import FastAPI, status
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from modules.auth.dependencies import current_user
from modules.users.api.api import get_microsoft_graph, get_uow, router
from modules.users.domain.entities.users import BlockedUser, User, UserRole
from modules.users.infrastructure.microsoft_graph import MicrosoftDirectoryUser
from shared.uow import UnitOfWork


def route_for(path: str, method: str) -> APIRoute:
    for route in router.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == path
            and method in (route.methods or set())
        ):
            return route
    raise AssertionError(f"Missing {method} {path} route")


def test_user_router_exposes_role_and_delete_routes():
    assert route_for("/users/{user_id}/role", "PATCH")
    assert route_for("/users/{user_id}", "DELETE").status_code == status.HTTP_204_NO_CONTENT


class Users:
    def __init__(self) -> None:
        self.blocked: list[BlockedUser] = []

    async def list_blocked(self) -> list[BlockedUser]:
        return self.blocked

    async def upsert_blocked(self, user: BlockedUser) -> None:
        self.blocked = [item for item in self.blocked if item.microsoft_oid != user.microsoft_oid]
        self.blocked.append(user)

    async def delete_blocked(self, microsoft_oid: str) -> None:
        self.blocked = [item for item in self.blocked if item.microsoft_oid != microsoft_oid]


class Uow:
    def __init__(self) -> None:
        self.users = Users()
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


class Graph:
    user = MicrosoftDirectoryUser("employee-oid", "employee@example.com", "Employee")

    def search_users(self, _query: str) -> list[MicrosoftDirectoryUser]:
        return [self.user]

    def get_user(self, _microsoft_oid: str) -> MicrosoftDirectoryUser:
        return self.user


def test_rrhh_can_search_block_and_unblock_microsoft_user() -> None:
    app = FastAPI()
    app.include_router(router)
    uow = Uow()
    rrhh = User("rrhh-oid", "rrhh@example.com", "RRHH", UserRole.RRHH)
    app.dependency_overrides[get_uow] = lambda: cast(UnitOfWork, cast(object, uow))
    app.dependency_overrides[current_user] = lambda: rrhh
    app.dependency_overrides[get_microsoft_graph] = Graph
    client = TestClient(app)

    result = client.get("/users/microsoft/search?q=employee")
    assert result.status_code == 200 and result.json()[0]["blocked"] is False

    result = client.put("/users/blocked/employee-oid")
    assert result.status_code == 200 and result.json()["name"] == "Employee"
    assert client.get("/users/blocked").json()[0]["microsoft_oid"] == "employee-oid"

    assert client.delete("/users/blocked/employee-oid").status_code == 204
    assert uow.users.blocked == []
    assert uow.commits == 2
