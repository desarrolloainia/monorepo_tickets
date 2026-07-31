from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class TicketRequestModel(Base):
    __tablename__ = "ticket_requests"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cantidad: Mapped[int] = mapped_column(Integer)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IssuedTicketModel(Base):
    __tablename__ = "issued_tickets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ticket_request_id: Mapped[UUID] = mapped_column(ForeignKey("ticket_requests.id"), index=True)
    codigo: Mapped[str] = mapped_column(String(11), unique=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class TicketCodeCounterModel(Base):
    __tablename__ = "ticket_code_counters"

    period: Mapped[str] = mapped_column(String(4), primary_key=True)
    last_sequence: Mapped[int] = mapped_column(Integer, default=0)


class TicketPriceConfigurationModel(Base):
    __tablename__ = "ticket_price_configurations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    updated_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
