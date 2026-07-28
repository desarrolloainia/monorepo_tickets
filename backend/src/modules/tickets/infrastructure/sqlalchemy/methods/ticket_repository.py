from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.infrastructure.sqlalchemy.persistence.models import TicketModel


class SQLAlchemyTicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(ticket_model: TicketModel) -> Ticket:
        return Ticket(
            id=ticket_model.id,
            title=ticket_model.title,
            nombre=ticket_model.title,
            description=ticket_model.description,
            status=ticket_model.status,
            codigo=ticket_model.codigo,
            codigo_qr=ticket_model.codigo_qr,
            fecha_emision=ticket_model.fecha_emision,
            fecha_creacion=ticket_model.fecha_creacion,
            cantidad=ticket_model.cantidad,
            aprobacion=ticket_model.aprobacion,
        )

    @staticmethod
    def _from_domain(ticket: Ticket) -> TicketModel:
        return TicketModel(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            codigo=ticket.codigo,
            codigo_qr=ticket.codigo_qr,
            fecha_emision=ticket.fecha_emision,
            fecha_creacion=ticket.fecha_creacion,
            cantidad=ticket.cantidad,
            aprobacion=ticket.aprobacion,
        )

    async def add(self, ticket: Ticket) -> Ticket:
        ticket_model = self._from_domain(ticket)
        ticket_model = await self.session.merge(ticket_model)
        await self.session.flush()
        return self._to_entity(ticket_model)

    async def remove(self, ticket_id: UUID) -> None:
        await self.session.execute(delete(TicketModel).where(TicketModel.id == ticket_id))

    async def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        ticket_model = await self.session.get(TicketModel, ticket_id)
        return None if ticket_model is None else self._to_entity(ticket_model)

    async def list_all(self) -> Sequence[Ticket]:
        result = await self.session.scalars(select(TicketModel))
        return [self._to_entity(ticket_model) for ticket_model in result]
