from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.users.api.dependencies import get_uow, require_approver
from modules.users.api.dtos import UserDTO, UserRoleUpdateDTO
from modules.users.application.delete_user import DeleteUser
from modules.users.application.get_user_by_id import GetUserById
from modules.users.application.update_user import UpdateUser
from modules.users.domain.entities.users import User
from shared.uow import UnitOfWork

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}/role", response_model=UserDTO)
async def edit_role(
    user_id: UUID,
    changes: UserRoleUpdateDTO,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_approver)],
) -> User:
    try:
        user = await GetUserById(unit_of_work).get_by_id(user_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    user.role = changes.role
    return await UpdateUser(unit_of_work).update(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_approver)],
) -> None:
    try:
        await DeleteUser(unit_of_work).delete(user_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
