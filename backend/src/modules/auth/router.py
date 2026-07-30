import asyncio
import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from modules.auth.config import (
    ACCESS_TOKEN_COOKIE,
    ACCESS_TOKEN_TTL_SECONDS,
    OAUTH_STATE_COOKIE,
    OAUTH_STATE_TTL_SECONDS,
    auth_settings,
)
from modules.auth.dependencies import current_user, get_uow
from modules.auth.internal_token_service import token_service
from modules.auth.microsoft import MicrosoftOAuth, microsoft_oauth
from modules.users.api.dtos import UserDTO
from modules.users.application.sync_microsoft_user import SyncMicrosoftUser
from modules.users.domain.entities.users import User
from shared.uow import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])


def get_microsoft_oauth() -> MicrosoftOAuth:
    return microsoft_oauth


@router.get("/microsoft/login")
async def microsoft_login(
    provider: Annotated[MicrosoftOAuth, Depends(get_microsoft_oauth)],
) -> RedirectResponse:
    state_value = secrets.token_urlsafe(32)
    try:
        url = await asyncio.to_thread(provider.authorization_url, state_value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
    response = RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state_value,
        max_age=OAUTH_STATE_TTL_SECONDS,
        httponly=True,
        secure=auth_settings.cookie_secure,
        samesite="lax",
    )
    return response


@router.get("/microsoft/callback")
async def microsoft_callback(
    request: Request,
    provider: Annotated[MicrosoftOAuth, Depends(get_microsoft_oauth)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    code: Annotated[str | None, Query()] = None,
    state_value: Annotated[str | None, Query(alias="state")] = None,
    error: Annotated[str | None, Query()] = None,
) -> RedirectResponse:
    expected_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if (
        not state_value
        or not expected_state
        or not secrets.compare_digest(state_value, expected_state)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        claims = await asyncio.to_thread(provider.exchange_code, code)
        microsoft_oid, email, name = _identity_from_claims(claims)
        user = await SyncMicrosoftUser(unit_of_work).sync(microsoft_oid, email, name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
    response = RedirectResponse(
        auth_settings.success_redirect_url, status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        token_service.create(user),
        max_age=ACCESS_TOKEN_TTL_SECONDS,
        httponly=True,
        secure=auth_settings.cookie_secure,
        samesite="lax",
    )
    response.delete_cookie(OAUTH_STATE_COOKIE)
    return response


def _identity_from_claims(claims: dict[str, Any]) -> tuple[str, str, str]:
    microsoft_oid = claims.get("oid") or claims.get("sub")
    email = claims.get("email") or claims.get("upn") or claims.get("preferred_username")
    if not microsoft_oid or not email:
        raise ValueError("Identidad Microsoft incompleta")
    return str(microsoft_oid), str(email), str(claims.get("name") or email)


@router.get("/me", response_model=UserDTO)
async def me(user: Annotated[User, Depends(current_user)]) -> User:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    response.delete_cookie(OAUTH_STATE_COOKIE)
    return response
