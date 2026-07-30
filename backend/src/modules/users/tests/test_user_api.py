from fastapi import status
from fastapi.routing import APIRoute

from modules.users.api.api import router


def route_for(path: str, method: str) -> APIRoute:
    for route in router.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == path
            and method in (route.methods or set())
        ):
            return route
    raise AssertionError(f"Missing {method} {path} route")


def test_user_router_exposes_role_and_delete_routes():
    assert route_for("/users/{user_id}/role", "PATCH")
    assert route_for("/users/{user_id}", "DELETE").status_code == status.HTTP_204_NO_CONTENT
