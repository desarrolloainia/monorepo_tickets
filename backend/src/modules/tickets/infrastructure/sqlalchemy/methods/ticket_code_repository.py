from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.infrastructure.sqlalchemy.persistence.models import TicketCodeCounterModel


class SqlAlchemyTicketCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def reserve_next_ticket_sequence(self, period: str) -> int:
        statement = (
            insert(TicketCodeCounterModel)
            .values(period=period, last_sequence=1)
            .on_conflict_do_update(
                index_elements=[TicketCodeCounterModel.period],
                set_={"last_sequence": TicketCodeCounterModel.last_sequence + 1},
            )
            .returning(TicketCodeCounterModel.last_sequence)
        )
        return (await self.session.execute(statement)).scalar_one()
