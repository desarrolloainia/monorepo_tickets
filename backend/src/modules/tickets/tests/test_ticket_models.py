from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modules.tickets.api.dtos import TicketCreateDTO, TicketDTO
from modules.tickets.infrastructure.sqlalchemy.persistence.models import TicketModel


def test_ticket_dtos_validate_input_and_serialize_orm_model():
    with pytest.raises(ValidationError):
        _ = TicketCreateDTO(title="", description="Detalle", cantidad=0)

    ticket_create = TicketCreateDTO(
        title="Concierto", description="Entrada general", cantidad=1
    )
    assert ticket_create.cantidad == 1

    ticket = TicketModel(
        id=uuid4(),
        title="Concierto",
        description="Entrada general",
        status="pending",
        codigo="ABC-123",
        codigo_qr="qr-data",
        fecha_emision=datetime.now().astimezone(),
        fecha_creacion=datetime.now().astimezone(),
        cantidad=1,
        aprobacion=False,
    )

    assert TicketDTO.model_validate(ticket).codigo == "ABC-123"
