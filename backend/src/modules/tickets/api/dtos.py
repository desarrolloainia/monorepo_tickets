from datetime import datetime
from decimal import Decimal
from typing import ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.tickets.domain.entities.ticket import TicketRequestStatus


class TicketRequestCreateDTO(BaseModel):
    cantidad: Literal[11, 22]


class TicketRequestDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    cantidad: int
    created_by_id: UUID
    fecha_creacion: datetime
    status: TicketRequestStatus
    approved_by_id: UUID | None
    approved_at: datetime | None


class PendingTicketRequestDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    requester_name: str
    cantidad: int
    fecha_creacion: datetime


class UserSpendingDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    user_id: UUID
    nombre: str
    email: str
    total_gastado: Decimal
    tickets_emitidos: int


class SpendingSummaryDTO(BaseModel):
    period: str
    total_gastado: Decimal
    tickets_emitidos: int
    gasto_medio_por_usuario: Decimal
    usuarios: list[UserSpendingDTO]


class SpendingRequestDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    fecha_emision: datetime
    tickets_emitidos: int
    total_gastado: Decimal


class UserSpendingDetailDTO(BaseModel):
    period: str
    user_id: UUID
    nombre: str
    email: str
    total_gastado: Decimal
    tickets_emitidos: int
    solicitudes: list[SpendingRequestDTO]


class TicketPriceUpdateDTO(BaseModel):
    precio_unitario: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    expected_configuration_id: UUID | None = None


class TicketPriceConfigurationDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    precio_unitario: Decimal
    updated_by_id: UUID
    updated_by_name: str
    updated_at: datetime


class TicketPriceOverviewDTO(BaseModel):
    precio_unitario: Decimal
    current_configuration_id: UUID | None
    historial: list[TicketPriceConfigurationDTO]
