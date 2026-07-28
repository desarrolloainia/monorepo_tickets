from fastapi import status
from fastapi.routing import APIRoute

from modules.tickets.api.api import router


def route_for(path: str, method: str) -> APIRoute:
    for route in router.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == path
            and method in (route.methods or set())
        ):
            return route
    raise AssertionError(f"Missing {method} {path} route")


def test_ticket_router_exposes_crud_and_approval_routes():
    assert route_for("/tickets/", "GET")
    assert route_for("/tickets/", "POST").status_code == status.HTTP_201_CREATED
    assert route_for("/tickets/{ticket_id}", "GET")
    assert route_for("/tickets/{ticket_id}", "DELETE").status_code == status.HTTP_204_NO_CONTENT
    assert route_for("/tickets/{ticket_id}/approve", "PATCH")
