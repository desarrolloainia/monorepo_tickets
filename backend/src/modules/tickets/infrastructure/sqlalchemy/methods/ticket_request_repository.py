from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.domain.entities.ticket import TicketRequest, TicketRequestStatus
from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from modules.tickets.infrastructure.sqlalchemy.persistence.models import (
    IssuedTicketModel,
    TicketCodeCounterModel,
    TicketPriceConfigurationModel,
    TicketRequestModel,
)


class SQLAlchemyTicketRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _to_request(model: TicketRequestModel) -> TicketRequest:
        return TicketRequest(
            id=model.id,
            cantidad=model.cantidad,
            created_by_id=model.created_by_id,
            fecha_creacion=model.fecha_creacion,
            status=TicketRequestStatus(model.status),
            approved_by_id=model.approved_by_id,
            approved_at=model.approved_at,
        )

    async def add(self, request: TicketRequest) -> TicketRequest:
        self.session.add(
            TicketRequestModel(
                id=request.id,
                cantidad=request.cantidad,
                created_by_id=request.created_by_id,
                fecha_creacion=request.fecha_creacion,
                status=request.status,
                approved_by_id=request.approved_by_id,
                approved_at=request.approved_at,
            )
        )
        await self.session.flush()
        return request

    async def find_by_id(
        self, request_id: UUID, *, for_update: bool = False
    ) -> TicketRequest | None:
        query = select(TicketRequestModel).where(TicketRequestModel.id == request_id)
        if for_update:
            query = query.with_for_update()
        model = await self.session.scalar(query)
        return None if model is None else self._to_request(model)

    async def list_by_creator(self, creator_id: UUID) -> Sequence[TicketRequest]:
        models = await self.session.scalars(
            select(TicketRequestModel).where(TicketRequestModel.created_by_id == creator_id)
        )
        return [self._to_request(model) for model in models]

    async def update(self, request: TicketRequest) -> None:
        model = await self.session.get(TicketRequestModel, request.id)
        if model is None:
            raise ValueError("Solicitud no encontrada")
        model.status = request.status
        model.approved_by_id = request.approved_by_id
        model.approved_at = request.approved_at
        await self.session.flush()

    async def current_price(self) -> Decimal | None:
        return await self.session.scalar(
            select(TicketPriceConfigurationModel.precio_unitario).order_by(
                desc(TicketPriceConfigurationModel.updated_at)
            )
        )

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

    async def add_issued(self, request_id: UUID, tickets: Sequence[PrintableTicket]) -> None:
        self.session.add_all(
            [
                IssuedTicketModel(
                    ticket_request_id=request_id,
                    codigo=ticket.codigo,
                    fecha_emision=ticket.fecha_emision,
                    precio_unitario=ticket.precio_unitario,
                )
                for ticket in tickets
            ]
        )
        await self.session.flush()

    async def list_issued(self, request_id: UUID) -> Sequence[PrintableTicket]:
        models = await self.session.scalars(
            select(IssuedTicketModel)
            .where(IssuedTicketModel.ticket_request_id == request_id)
            .order_by(IssuedTicketModel.codigo)
        )
        return [
            PrintableTicket("", model.codigo, model.fecha_emision, model.precio_unitario)
            for model in models
        ]
