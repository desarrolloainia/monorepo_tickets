import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from modules.users.api.dependencies import get_uow, require_approver, require_rrhh
from modules.users.api.dtos import BlockedUserDTO, MicrosoftUserDTO, UserDTO, UserRoleUpdateDTO
from modules.users.application.delete_user import DeleteUser
from modules.users.application.get_user_by_id import GetUserById
from modules.users.application.update_user import UpdateUser
from modules.users.domain.entities.users import BlockedUser, User
from modules.users.infrastructure.microsoft_graph import (
    MicrosoftGraph,
    MicrosoftGraphError,
    MicrosoftUserNotFound,
    microsoft_graph,
)
from shared.uow import UnitOfWork

router = APIRouter(prefix="/users", tags=["users"])


def get_microsoft_graph() -> MicrosoftGraph:
    return microsoft_graph


@router.get("/microsoft/search", response_model=list[MicrosoftUserDTO])
async def search_microsoft_users(
    q: Annotated[str, Query(min_length=2, max_length=100)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_rrhh)],
    graph: Annotated[MicrosoftGraph, Depends(get_microsoft_graph)],
) -> list[MicrosoftUserDTO]:
    query = q.strip()
    if len(query) < 2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        users = await asyncio.to_thread(graph.search_users, query)
    except MicrosoftGraphError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo consultar Microsoft 365",
        ) from error
    blocked = {user.microsoft_oid for user in await unit_of_work.users.list_blocked()}
    return [
        MicrosoftUserDTO(
            microsoft_oid=user.microsoft_oid,
            email=user.email,
            name=user.name,
            blocked=user.microsoft_oid in blocked,
        )
        for user in users
    ]


@router.get("/blocked", response_model=list[BlockedUserDTO])
async def list_blocked_users(
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_rrhh)],
) -> list[BlockedUser]:
    return await unit_of_work.users.list_blocked()


@router.put("/blocked/{microsoft_oid}", response_model=BlockedUserDTO)
async def block_user(
    microsoft_oid: str,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    rrhh: Annotated[User, Depends(require_rrhh)],
    graph: Annotated[MicrosoftGraph, Depends(get_microsoft_graph)],
) -> BlockedUser:
    if microsoft_oid == rrhh.microsoft_oid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes bloquear tu propio acceso",
        )
    try:
        directory_user = await asyncio.to_thread(graph.get_user, microsoft_oid)
    except MicrosoftUserNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario ya no existe en Microsoft 365",
        ) from error
    except MicrosoftGraphError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo consultar Microsoft 365",
        ) from error
    blocked_user = BlockedUser(
        directory_user.microsoft_oid,
        directory_user.email,
        directory_user.name,
    )
    await unit_of_work.users.upsert_blocked(blocked_user)
    await unit_of_work.commit()
    return blocked_user


@router.delete("/blocked/{microsoft_oid}", status_code=status.HTTP_204_NO_CONTENT)
async def unblock_user(
    microsoft_oid: str,
    unit_of_work: Annotated[UnitOfWork, Depends(get_uow)],
    _: Annotated[User, Depends(require_rrhh)],
) -> None:
    await unit_of_work.users.delete_blocked(microsoft_oid)
    await unit_of_work.commit()


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
