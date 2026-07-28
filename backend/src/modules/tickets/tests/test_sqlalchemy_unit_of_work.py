from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.uow import UnitOfWork


class Session:
    def __init__(self):
        self.committed: bool = False
        self.rolled_back: bool = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

def as_async_session(session: Session) -> AsyncSession:
    return cast(AsyncSession, cast(object, session))


async def test_shared_unit_of_work_confirma_la_sesion():
    session = Session()

    async with UnitOfWork(as_async_session(session)) as unit_of_work:
        assert unit_of_work.tickets is not None

    assert session.committed and not session.rolled_back


async def test_shared_unit_of_work_revierte_ante_un_error():
    session = Session()

    with pytest.raises(ValueError):
        async with UnitOfWork(as_async_session(session)):
            raise ValueError

    assert session.rolled_back and not session.committed
