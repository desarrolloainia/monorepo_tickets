from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

import jwt
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from modules.auth.config import (
    ACCESS_TOKEN_COOKIE,
    JWT_AUDIENCE,
    JWT_ISSUER,
    OAUTH_STATE_COOKIE,
    auth_settings,
)
from modules.auth.dependencies import get_uow
from modules.auth.internal_token_service import token_service
from modules.auth.router import get_microsoft_oauth, router
from modules.users.domain.entities.users import User, UserRole
from shared.uow import UnitOfWork


class Users:
    def __init__(self) -> None:
        self.user: User | None = None

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.user if self.user and self.user.id == user_id else None

    async def get_by_microsoft_oid(self, microsoft_oid: str) -> User | None:
        return self.user if self.user and self.user.microsoft_oid == microsoft_oid else None

    async def add(self, user: User) -> None:
        self.user = user

    async def update(self, user: User) -> None:
        self.user = user


class FakeUow:
    def __init__(self) -> None:
        self.users = Users()
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


class Provider:
    def __init__(self, claims: dict[str, Any] | None = None, error: bool = False) -> None:
        self.claims = claims or {
            "oid": "microsoft-oid",
            "email": "user@example.com",
            "name": "User",
        }
        self.error = error

    def authorization_url(self, state_value: str) -> str:
        return f"https://login.microsoftonline.com/authorize?state={state_value}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        if self.error:
            raise ValueError("Microsoft error")
        assert code == "code"
        return self.claims


def as_uow(value: FakeUow) -> UnitOfWork:
    return cast(UnitOfWork, cast(object, value))


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    monkeypatch.setattr(auth_settings, "cookie_secure", False)
    application = FastAPI()
    application.include_router(router)
    return application


def configure(app: FastAPI, provider: Provider, uow: FakeUow) -> TestClient:
    app.dependency_overrides[get_microsoft_oauth] = lambda: provider
    app.dependency_overrides[get_uow] = lambda: as_uow(uow)
    return TestClient(app)


def test_login_redirects_and_sets_http_only_state_cookie(app: FastAPI) -> None:
    client = configure(app, Provider(), FakeUow())
    response = client.get("/auth/microsoft/login", follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"].startswith("https://login.microsoftonline.com/")
    assert response.cookies.get(OAUTH_STATE_COOKIE)
    assert "HttpOnly" in response.headers["set-cookie"]


def callback(client: TestClient, state_value: str = "state"):
    client.cookies.set(OAUTH_STATE_COOKIE, "state")
    return client.get(
        f"/auth/microsoft/callback?code=code&state={state_value}", follow_redirects=False
    )


def test_callback_creates_then_updates_user_and_session(app: FastAPI) -> None:
    uow = FakeUow()
    provider = Provider()
    client = configure(app, provider, uow)

    response = callback(client)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.cookies.get(ACCESS_TOKEN_COOKIE)
    assert uow.users.user and uow.users.user.role == UserRole.USER

    provider.claims.update(email="updated@example.com", name="Updated")
    callback(client)
    assert uow.users.user.email == "updated@example.com"
    assert uow.users.user.name == "Updated"
    assert uow.commits == 2


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/auth/microsoft/callback?code=code&state=wrong", 401),
        ("/auth/microsoft/callback?state=state", 400),
        ("/auth/microsoft/callback?error=denied&state=state", 401),
    ],
)
def test_callback_rejects_invalid_requests(app: FastAPI, path: str, expected: int) -> None:
    client = configure(app, Provider(), FakeUow())
    client.cookies.set(OAUTH_STATE_COOKIE, "state")
    assert client.get(path).status_code == expected


@pytest.mark.parametrize("provider", [Provider(error=True), Provider({"oid": "oid"})])
def test_callback_rejects_microsoft_errors_and_incomplete_claims(
    app: FastAPI, provider: Provider
) -> None:
    assert callback(configure(app, provider, FakeUow())).status_code == 401


def test_token_contains_only_session_claims_and_rejects_expired() -> None:
    user = User("oid", "user@example.com", "User")
    claims = token_service.decode(token_service.create(user))
    assert set(claims) == {"sub", "iat", "exp", "iss", "aud"}

    now = datetime.now(UTC)
    expired = jwt.encode(
        {
            "sub": str(user.id),
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
        },
        auth_settings.cookie_secret,
        algorithm="HS256",
    )
    with pytest.raises(ValueError):
        token_service.decode(expired)


def test_me_accepts_only_valid_cookie_and_existing_user(app: FastAPI) -> None:
    uow = FakeUow()
    uow.users.user = User("oid", "user@example.com", "User")
    client = configure(app, Provider(), uow)

    assert client.get("/auth/me").status_code == 401
    client.cookies.set(ACCESS_TOKEN_COOKIE, "manipulated")
    assert client.get("/auth/me").status_code == 401
    client.cookies.set(ACCESS_TOKEN_COOKIE, token_service.create(uow.users.user))
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "user"

    uow.users.user = None
    assert client.get("/auth/me").status_code == 401


def test_logout_deletes_both_cookies(app: FastAPI) -> None:
    client = TestClient(app)
    response = client.post("/auth/logout")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ACCESS_TOKEN_COOKIE in response.headers["set-cookie"]
    assert OAUTH_STATE_COOKIE in response.headers["set-cookie"]
