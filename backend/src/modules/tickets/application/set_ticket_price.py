from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from modules.tickets.domain.entities.ticket_price import TicketPriceConfiguration
from shared.uow import UnitOfWork


class SetTicketPrice:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    async def set(
        self,
        price: Decimal,
        updated_by_id: UUID,
        updated_by_name: str,
        expected_configuration_id: UUID | None,
    ) -> TicketPriceConfiguration:
        current = await self.uow.ticket_requests.current_price_configuration(for_update=True)
        if (current.id if current else None) != expected_configuration_id:
            raise ValueError("La tarifa ha cambiado; recarga antes de volver a intentarlo")

        configuration = TicketPriceConfiguration(
            precio_unitario=price,
            updated_by_id=updated_by_id,
            updated_at=datetime.now(UTC),
            updated_by_name=updated_by_name,
        )
        await self.uow.ticket_requests.add_price_configuration(configuration)
        await self.uow.commit()
        return configuration
