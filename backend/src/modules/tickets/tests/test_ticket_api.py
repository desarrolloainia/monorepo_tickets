import pytest
from fastapi.routing import APIRoute
from pydantic import ValidationError

from modules.tickets.api.api import router
from modules.tickets.api.dtos import TicketRequestCreateDTO


def test_ticket_router_has_approval_but_no_edit_route() -> None:
    routes = {
        (route.path, method)
        for route in router.routes
        if isinstance(route, APIRoute)
        for method in route.methods or set()
    }

    assert ("/tickets/{ticket_request_id}/approve", "POST") in routes
    assert ("/tickets/{ticket_request_id}", "PATCH") not in routes
    assert ("/tickets/{ticket_request_id}", "PUT") not in routes


def test_ticket_request_only_accepts_supported_quantities() -> None:
    assert TicketRequestCreateDTO(cantidad=11).cantidad == 11
    assert TicketRequestCreateDTO(cantidad=22).cantidad == 22

    with pytest.raises(ValidationError):
        TicketRequestCreateDTO.model_validate({"cantidad": 12})
