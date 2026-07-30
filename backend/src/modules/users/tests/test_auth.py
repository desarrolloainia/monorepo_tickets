import pytest
from fastapi import HTTPException, status

from modules.users.api.dependencies import require_approver
from modules.users.domain.entities.users import User, UserRole


def test_only_approvers_are_authorized() -> None:
    approver = User("oid", "user@example.com", "User", role=UserRole.APPROVER)
    assert require_approver(approver) is approver

    with pytest.raises(HTTPException) as error:
        require_approver(User("oid", "user@example.com", "User"))
    assert error.value.status_code == status.HTTP_403_FORBIDDEN
