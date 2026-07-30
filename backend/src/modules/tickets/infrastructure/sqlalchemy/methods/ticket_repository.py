from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.domain.entities.ticket import Ticket
from modules.tickets.infrastructure.sqlalchemy.persistence.models import TicketModel


class SQLAlchemyTicketRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

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
            created_by_id=ticket_model.created_by_id,
            approved_by_id=ticket_model.approved_by_id,
            approved_at=ticket_model.approved_at,
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
            created_by_id=ticket.created_by_id,
            approved_by_id=ticket.approved_by_id,
            approved_at=ticket.approved_at,
        )

    async def add(self, ticket: Ticket) -> Ticket:
        ticket_model = self._from_domain(ticket)
        ticket_model = await self.session.merge(ticket_model)
        await self.session.flush()
        return self._to_entity(ticket_model)

    async def remove(self, ticket_id: UUID, created_by_id: UUID | None = None) -> None:
        query = delete(TicketModel).where(TicketModel.id == ticket_id)
        if created_by_id is not None:
            query = query.where(TicketModel.created_by_id == created_by_id)
        _ = await self.session.execute(query)

    async def find_by_id(
        self, ticket_id: UUID, created_by_id: UUID | None = None
    ) -> Ticket | None:
        query = select(TicketModel).where(TicketModel.id == ticket_id)
        if created_by_id is not None:
            query = query.where(TicketModel.created_by_id == created_by_id)
        ticket_model = await self.session.scalar(query)
        return None if ticket_model is None else self._to_entity(ticket_model)

    async def list_all(self, created_by_id: UUID | None = None) -> Sequence[Ticket]:
        query = select(TicketModel)
        if created_by_id is not None:
            query = query.where(TicketModel.created_by_id == created_by_id)
        result = await self.session.scalars(query)
        return [self._to_entity(ticket_model) for ticket_model in result]
