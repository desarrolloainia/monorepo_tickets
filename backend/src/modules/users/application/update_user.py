from datetime import UTC, datetime

from modules.users.domain.entities.users import User
from shared import uow


class UpdateUser:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def update(self, user: User) -> User:
        if await self.uow.users.get_by_id(user.id) is None:
            raise ValueError("Usuario no encontrado")
        user.updated_at = datetime.now(UTC)
        await self.uow.users.update(user)
        await self.uow.commit()
        return user
