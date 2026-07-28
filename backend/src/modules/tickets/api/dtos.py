from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TicketCreateDTO(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    cantidad: int = Field(ge=1)


class TicketDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    status: str
    codigo: str
    codigo_qr: str
    fecha_emision: datetime
    fecha_creacion: datetime
    cantidad: int
    aprobacion: bool

