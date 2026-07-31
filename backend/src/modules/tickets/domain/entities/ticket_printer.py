from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PrintableTicket:
    nombre_persona: str
    codigo: str
    fecha_emision: datetime
    precio_unitario: Decimal
