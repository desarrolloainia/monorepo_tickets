from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.dependencies import current_user
from modules.users.domain.entities.users import User, UserRole
from shared.database import get_db
from shared.uow import UnitOfWork


async def get_uow(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncIterator[UnitOfWork]:
    yield UnitOfWork(db)


def require_approver(user: Annotated[User, Depends(current_user)]) -> User:
    if user.role != UserRole.APPROVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol approver"
        )
    return user
