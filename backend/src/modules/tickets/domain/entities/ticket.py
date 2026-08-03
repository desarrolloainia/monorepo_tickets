from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class TicketRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class TicketRequest:
    cantidad: int
    created_by_id: UUID
    fecha_creacion: datetime

    id: UUID = field(default_factory=uuid4)
    status: TicketRequestStatus = TicketRequestStatus.PENDING
    approved_by_id: UUID | None = None
    approved_at: datetime | None = None


@dataclass(frozen=True)
class PendingTicketRequest:
    id: UUID
    requester_name: str
    cantidad: int
    fecha_creacion: datetime
