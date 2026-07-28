from datetime import datetime

from modules.tickets.domain.ports.ticket_code_repository import TicketCodeRepository


class TicketCodeUseCase:
    def __init__(self, repository: TicketCodeRepository):
        self.repository = repository

    async def generar_codigo(self, fecha_emision: datetime) -> str:
        period = fecha_emision.strftime("%y%m")
        sequence = await self.repository.reserve_next_ticket_sequence(period)
        if not 1 <= sequence <= 999_999:
            raise ValueError(f"Serie agotada para el periodo {period}")
        return f"{period}-{sequence:06d}"
