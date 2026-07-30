from typing import cast, final
from uuid import UUID

import pytest

from modules.users.application.create_user import CreateUser
from modules.users.application.delete_user import DeleteUser
from modules.users.application.get_user_by_id import GetUserById
from modules.users.application.list_users import ListUsers
from modules.users.application.sync_microsoft_user import SyncMicrosoftUser
from modules.users.application.update_user import UpdateUser
from modules.users.domain.entities.users import User, UserRole
from shared.uow import UnitOfWork


@final
class Users:
    def __init__(self) -> None:
        self.values: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        self.values[user.id] = user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.values.get(user_id)

    async def get_by_microsoft_oid(self, microsoft_oid: str) -> User | None:
        return next(
            (user for user in self.values.values() if user.microsoft_oid == microsoft_oid), None
        )

    async def list_all(self) -> list[User]:
        return list(self.values.values())

    async def update(self, user: User) -> None:
        self.values[user.id] = user

    async def delete(self, user_id: UUID) -> None:
        del self.values[user_id]


@final
class UsersUnitOfWork:
    def __init__(self) -> None:
        self.users = Users()
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


def as_uow(value: UsersUnitOfWork) -> UnitOfWork:
    return cast(UnitOfWork, cast(object, value))


async def test_user_use_cases_create_read_update_and_delete():
    unit_of_work = UsersUnitOfWork()
    user = User(microsoft_oid="oid", email="user@example.com", name="User")

    assert await CreateUser(as_uow(unit_of_work)).create(user) is user
    assert await GetUserById(as_uow(unit_of_work)).get_by_id(user.id) is user
    assert await ListUsers(as_uow(unit_of_work)).list() == [user]

    user.name = "Updated User"
    user.role = UserRole.APPROVER
    assert await UpdateUser(as_uow(unit_of_work)).update(user) is user
    await DeleteUser(as_uow(unit_of_work)).delete(user.id)

    assert unit_of_work.commits == 3
    assert user.role == UserRole.APPROVER
    with pytest.raises(ValueError, match="Usuario no encontrado"):
        _ = await GetUserById(as_uow(unit_of_work)).get_by_id(user.id)


async def test_sync_microsoft_user_creates_updates_and_reuses_user():
    unit_of_work = UsersUnitOfWork()
    sync_user = SyncMicrosoftUser(as_uow(unit_of_work))

    created = await sync_user.sync("oid", "user@example.com", "User")
    updated = await sync_user.sync("oid", "updated@example.com", "Updated User")
    reused = await sync_user.sync("oid", "updated@example.com", "Updated User")

    assert created is updated is reused
    assert reused.email == "updated@example.com" and reused.name == "Updated User"
    assert unit_of_work.commits == 2
