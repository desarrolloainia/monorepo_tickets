from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tickets.domain.entities.ticket import (
    PendingTicketRequest,
    SpendingRequest,
    TicketRequest,
    TicketRequestStatus,
    UserSpending,
)
from modules.tickets.domain.entities.ticket_price import TicketPriceConfiguration
from modules.tickets.domain.entities.ticket_printer import PrintableTicket
from modules.tickets.infrastructure.sqlalchemy.persistence.models import (
    IssuedTicketModel,
    TicketCodeCounterModel,
    TicketPriceConfigurationModel,
    TicketRequestModel,
)
from modules.users.infrastructure.sqlalchemy.persistence.models import UserModel


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
        configuration = await self.current_price_configuration()
        return None if configuration is None else configuration.precio_unitario

    async def current_price_configuration(
        self, *, for_update: bool = False
    ) -> TicketPriceConfiguration | None:
        if for_update:
            # Serializes price changes even before the first configuration exists.
            await self.session.execute(select(func.pg_advisory_xact_lock(7_411_401)))
        query = (
            select(TicketPriceConfigurationModel, UserModel.name)
            .join(UserModel, TicketPriceConfigurationModel.updated_by_id == UserModel.id)
            .order_by(
                desc(TicketPriceConfigurationModel.updated_at),
                desc(TicketPriceConfigurationModel.id),
            )
            .limit(1)
        )
        if for_update:
            query = query.with_for_update(of=TicketPriceConfigurationModel)
        row = (await self.session.execute(query)).first()
        if row is None:
            return None
        model, updated_by_name = row
        return TicketPriceConfiguration(
            id=model.id,
            precio_unitario=model.precio_unitario,
            updated_by_id=model.updated_by_id,
            updated_at=model.updated_at,
            updated_by_name=updated_by_name,
        )

    async def list_price_configurations(
        self, limit: int = 10
    ) -> list[TicketPriceConfiguration]:
        rows = await self.session.execute(
            select(TicketPriceConfigurationModel, UserModel.name)
            .join(UserModel, TicketPriceConfigurationModel.updated_by_id == UserModel.id)
            .order_by(
                desc(TicketPriceConfigurationModel.updated_at),
                desc(TicketPriceConfigurationModel.id),
            )
            .limit(limit)
        )
        return [
            TicketPriceConfiguration(
                id=model.id,
                precio_unitario=model.precio_unitario,
                updated_by_id=model.updated_by_id,
                updated_at=model.updated_at,
                updated_by_name=updated_by_name,
            )
            for model, updated_by_name in rows
        ]

    async def add_price_configuration(
        self, configuration: TicketPriceConfiguration
    ) -> TicketPriceConfiguration:
        self.session.add(
            TicketPriceConfigurationModel(
                id=configuration.id,
                precio_unitario=configuration.precio_unitario,
                updated_by_id=configuration.updated_by_id,
                updated_at=configuration.updated_at,
            )
        )
        await self.session.flush()
        return configuration

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

    async def list_pending(self) -> list[PendingTicketRequest]:
        rows = await self.session.execute(
            select(
                TicketRequestModel.id,
                UserModel.name,
                TicketRequestModel.cantidad,
                TicketRequestModel.fecha_creacion,
            )
            .join(UserModel, TicketRequestModel.created_by_id == UserModel.id)
            .where(
                TicketRequestModel.status == TicketRequestStatus.PENDING,
            )
            .order_by(TicketRequestModel.fecha_creacion)
        )
        return [PendingTicketRequest(*row) for row in rows]

    async def spending_by_user(self, start: datetime, end: datetime) -> list[UserSpending]:
        spending = (
            select(
                TicketRequestModel.created_by_id.label("user_id"),
                func.sum(IssuedTicketModel.precio_unitario).label("total_gastado"),
                func.count(IssuedTicketModel.id).label("tickets_emitidos"),
            )
            .join(
                IssuedTicketModel,
                IssuedTicketModel.ticket_request_id == TicketRequestModel.id,
            )
            .where(
                TicketRequestModel.status == TicketRequestStatus.APPROVED,
                IssuedTicketModel.fecha_emision >= start,
                IssuedTicketModel.fecha_emision < end,
            )
            .group_by(TicketRequestModel.created_by_id)
            .subquery()
        )
        rows = await self.session.execute(
            select(
                UserModel.id,
                UserModel.name,
                UserModel.email,
                func.coalesce(spending.c.total_gastado, Decimal("0.00")),
                func.coalesce(spending.c.tickets_emitidos, 0),
            )
            .outerjoin(spending, spending.c.user_id == UserModel.id)
            .order_by(UserModel.name, UserModel.id)
        )
        return [UserSpending(*row) for row in rows]

    async def spending_requests(
        self, user_id: UUID, start: datetime, end: datetime
    ) -> list[SpendingRequest]:
        rows = await self.session.execute(
            select(
                TicketRequestModel.id,
                func.min(IssuedTicketModel.fecha_emision),
                func.count(IssuedTicketModel.id),
                func.sum(IssuedTicketModel.precio_unitario),
            )
            .join(
                IssuedTicketModel,
                IssuedTicketModel.ticket_request_id == TicketRequestModel.id,
            )
            .where(
                TicketRequestModel.created_by_id == user_id,
                TicketRequestModel.status == TicketRequestStatus.APPROVED,
                IssuedTicketModel.fecha_emision >= start,
                IssuedTicketModel.fecha_emision < end,
            )
            .group_by(TicketRequestModel.id)
            .order_by(desc(func.min(IssuedTicketModel.fecha_emision)), TicketRequestModel.id)
        )
        return [SpendingRequest(*row) for row in rows]
