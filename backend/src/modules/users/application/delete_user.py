from uuid import UUID

from shared import uow


class DeleteUser:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def delete(self, user_id: UUID) -> None:
        if await self.uow.users.get_by_id(user_id) is None:
            raise ValueError("Usuario no encontrado")
        await self.uow.users.delete(user_id)
        await self.uow.commit()
