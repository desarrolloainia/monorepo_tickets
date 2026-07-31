from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class TicketPriceConfiguration:
    precio_unitario: Decimal
    updated_by_id: UUID
    updated_at: datetime

    id: UUID = field(default_factory=uuid4)
