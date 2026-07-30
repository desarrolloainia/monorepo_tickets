from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.config import ACCESS_TOKEN_COOKIE
from modules.auth.internal_token_service import token_service
from modules.users.domain.entities.users import User
from shared.database import get_db
from shared.uow import UnitOfWork


async def get_uow(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncIterator[UnitOfWork]:
    yield UnitOfWork(db)


async def current_user(
    request: Request,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
) -> User:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        user_id = UUID(str(token_service.decode(token)["sub"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
    user = await unit_of_work.users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
