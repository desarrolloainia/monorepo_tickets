from datetime import UTC, datetime
from uuid import UUID

from modules.tickets.domain.entities.ticket import TicketRequest
from modules.tickets.domain.entities.annual_limit import AnnualLimitExceeded
from modules.tickets.application.date_ranges import MADRID, date_range
from shared.uow import UnitOfWork


class CreateTicketRequest:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def create(self, cantidad: int, created_by_id: UUID) -> TicketRequest:
        if cantidad not in (11, 22):
            raise ValueError("La cantidad debe ser 11 o 22.")
        configuration = await self.uow.ticket_requests.annual_limit(lock=True)
        await self.uow.ticket_requests.lock_employee(created_by_id)
        request = TicketRequest(cantidad, created_by_id, datetime.now(UTC))
        _, start, end = date_range(str(request.fecha_creacion.astimezone(MADRID).year))
        consumed = await self.uow.ticket_requests.annual_consumption(created_by_id, start, end)
        maximum = configuration.cantidad_maxima
        if maximum is not None and consumed + cantidad > maximum:
            raise AnnualLimitExceeded(maximum, consumed, cantidad)
        await self.uow.ticket_requests.add(request)
        await self.uow.commit()
        return request
