from modules.users.domain.entities.users import User
from shared import uow


class CreateUser:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def create(self, user: User) -> User:
        await self.uow.users.add(user)
        await self.uow.commit()
        return user
