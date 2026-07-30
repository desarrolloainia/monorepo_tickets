from modules.users.domain.entities.users import User
from shared import uow


class ListUsers:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def list(self) -> list[User]:
        return await self.uow.users.list_all()
