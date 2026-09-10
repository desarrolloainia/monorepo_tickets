from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AnnualLimit:
    cantidad_maxima: int | None = None
    updated_by_id: UUID | None = None
    updated_at: datetime | None = None


class AnnualLimitExceeded(ValueError):
    def __init__(self, maximum: int, consumed: int, requested: int):
        super().__init__(
            f"Máximo anual: {maximum}. Cantidad solicitada acumulada: {consumed + requested}. "
            f"Saldo disponible: {max(0, maximum - consumed)}."
        )
