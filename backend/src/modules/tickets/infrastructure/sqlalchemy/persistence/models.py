import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class TicketModel(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String(50))
    codigo: Mapped[str] = mapped_column(String(255), unique=True)
    codigo_qr: Mapped[str] = mapped_column(String(255), unique=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cantidad: Mapped[int] = mapped_column(Integer)
    aprobacion: Mapped[bool] = mapped_column(Boolean)
    # ponytail: nullable until existing tickets can be backfilled with a creator.
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TicketCodeCounterModel(Base):
    __tablename__ = "ticket_code_counters"

    period: Mapped[str] = mapped_column(String(4), primary_key=True)
    last_sequence: Mapped[int] = mapped_column(Integer, default=0)
