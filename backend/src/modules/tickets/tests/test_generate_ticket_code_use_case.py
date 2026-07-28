import asyncio
from datetime import datetime

import pytest

from modules.tickets.application.generate_ticket_code_use_case import TicketCodeUseCase


class Repository:
    def __init__(self):
        self.sequences: dict[str, int] = {}
        self.lock = asyncio.Lock()

    async def reserve_next_ticket_sequence(self, period: str) -> int:
        async with self.lock:
            sequence = self.sequences.get(period, 0) + 1
            self.sequences[period] = sequence
            return sequence


async def test_generar_codigo_usa_el_periodo_de_emision_y_secuencia_mensual():
    use_case = TicketCodeUseCase(Repository())

    assert await use_case.generar_codigo(datetime(2026, 7, 1)) == "2607-000001"
    assert await use_case.generar_codigo(datetime(2026, 7, 31)) == "2607-000002"
    assert await use_case.generar_codigo(datetime(2026, 8, 1)) == "2608-000001"


async def test_generar_codigo_reserva_series_distintas_en_peticiones_simultaneas():
    use_case = TicketCodeUseCase(Repository())

    codes = await asyncio.gather(
        *(use_case.generar_codigo(datetime(2026, 7, 1)) for _ in range(2))
    )

    assert set(codes) == {"2607-000001", "2607-000002"}


async def test_generar_codigo_falla_con_una_serie_fuera_de_rango():
    class ExhaustedRepository:
        async def reserve_next_ticket_sequence(self, period: str) -> int:
            return 1_000_000

    with pytest.raises(ValueError, match="Serie agotada para el periodo 2607"):
        await TicketCodeUseCase(ExhaustedRepository()).generar_codigo(datetime(2026, 7, 1))
