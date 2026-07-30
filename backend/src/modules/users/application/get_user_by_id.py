from uuid import UUID

from modules.users.domain.entities.users import User
from shared import uow


class GetUserById:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.uow.users.get_by_id(user_id)
        if user is None:
            raise ValueError("Usuario no encontrado")
        return user
