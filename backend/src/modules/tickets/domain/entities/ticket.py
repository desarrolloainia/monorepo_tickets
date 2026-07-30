from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Ticket:
    title: str
    nombre: str
    description: str
    status: str
    codigo: str
    codigo_qr: str
    fecha_emision: datetime
    fecha_creacion: datetime
    cantidad: int
    aprobacion: bool
    id: UUID = field(default_factory=uuid4)
    created_by_id: UUID | None = None
    approved_by_id: UUID | None = None
    approved_at: datetime | None = None
