from datetime import UTC, datetime

from modules.users.domain.entities.users import User
from shared import uow


class SyncMicrosoftUser:
    def __init__(self, unit_of_work: uow.UnitOfWork) -> None:
        self.uow: uow.UnitOfWork = unit_of_work

    async def sync(self, microsoft_oid: str, email: str, name: str) -> User:
        user = await self.uow.users.get_by_microsoft_oid(microsoft_oid)
        if user is None:
            user = User(microsoft_oid=microsoft_oid, email=email, name=name)
            await self.uow.users.add(user)
        elif user.email != email or user.name != name:
            user.email = email
            user.name = name
            user.updated_at = datetime.now(UTC)
            await self.uow.users.update(user)
        else:
            return user
        await self.uow.commit()
        return user
