from datetime import datetime

from modules.tickets.domain.ports.ticket_request_repository import TicketCodeRepository


class GenerateTicketCode:
    def __init__(self, repository: TicketCodeRepository) -> None:
        self.repository = repository

    async def generate(self, issued_at: datetime) -> str:
        period = issued_at.strftime("%y%m")
        sequence = await self.repository.reserve_next_ticket_sequence(period)
        if not 1 <= sequence <= 999_999:
            raise ValueError(f"Serie agotada para el periodo {period}")
        return f"{period}-{sequence:06d}"
