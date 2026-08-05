from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

DEFAULT_TICKET_PRICE = Decimal("5.50")


@dataclass
class TicketPriceConfiguration:
    precio_unitario: Decimal
    updated_by_id: UUID
    updated_at: datetime
    updated_by_name: str = ""
    id: UUID = field(default_factory=uuid4)
