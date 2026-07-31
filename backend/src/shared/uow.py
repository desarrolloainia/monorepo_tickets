from types import TracebackType
from typing import Self, cast

from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.domain.ports.ticket_request_repository import (
    TicketCodeRepository,
    TicketRequestRepository,
)
from modules.tickets.infrastructure.sqlalchemy.methods.ticket_request_repository import (
    SQLAlchemyTicketRequestRepository,
)
from modules.users.domain.ports.user_repository import UserRepository
from modules.users.infrastructure.sqlalchemy.methods.user_repository import (
    SQLAlchemyUserRepository,
)


class UnitOfWork:
    # por cada modulo con repository creado se añade al constructor
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
        self.ticket_requests: TicketRequestRepository = cast(
            TicketRequestRepository, SQLAlchemyTicketRequestRepository(session)
        )
        self.ticket_codes: TicketCodeRepository = cast(
            TicketCodeRepository, SQLAlchemyTicketRequestRepository(session)
        )
        self.users: UserRepository = cast(UserRepository, SQLAlchemyUserRepository(session))

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
