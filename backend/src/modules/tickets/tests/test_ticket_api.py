from fastapi.routing import APIRoute

from modules.tickets.api.api import router


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
