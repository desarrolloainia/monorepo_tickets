from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.tickets.domain.entities.ticket import TicketRequestStatus


class TicketRequestCreateDTO(BaseModel):
    cantidad: int = Field(ge=1)


class TicketRequestDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    cantidad: int
    created_by_id: UUID
    fecha_creacion: datetime
    status: TicketRequestStatus
    approved_by_id: UUID | None
    approved_at: datetime | None
