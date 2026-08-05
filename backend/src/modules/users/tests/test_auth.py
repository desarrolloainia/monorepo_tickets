import pytest
from fastapi import HTTPException, status

from modules.users.api.dependencies import (
    require_accountant,
    require_approver,
    require_rrhh,
    require_spending_access,
)
from modules.users.domain.entities.users import User, UserRole


def test_only_approvers_are_authorized() -> None:
    approver = User("oid", "user@example.com", "User", role=UserRole.APPROVER)
    assert require_approver(approver) is approver

    for role in (UserRole.USER, UserRole.RRHH):
        with pytest.raises(HTTPException) as error:
            require_approver(User("oid", "user@example.com", "User", role=role))
        assert error.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("role", [UserRole.USER, UserRole.APPROVER])
def test_only_rrhh_is_authorized(role: UserRole) -> None:
    rrhh = User("rrhh", "rrhh@example.com", "RRHH", role=UserRole.RRHH)
    assert require_rrhh(rrhh) is rrhh

    with pytest.raises(HTTPException) as error:
        require_rrhh(User("oid", "user@example.com", "User", role=role))
    assert error.value.status_code == status.HTTP_403_FORBIDDEN


def test_rrhh_and_accountant_can_read_spending() -> None:
    for role in (UserRole.RRHH, UserRole.ACCOUNTANT):
        user = User("oid", "user@example.com", "User", role=role)
        assert require_spending_access(user) is user

    with pytest.raises(HTTPException) as error:
        require_spending_access(User("oid", "user@example.com", "User"))
    assert error.value.status_code == status.HTTP_403_FORBIDDEN


def test_only_accountant_can_update_prices() -> None:
    accountant = User(
        "accountant", "accountant@example.com", "Accountant", role=UserRole.ACCOUNTANT
    )
    assert require_accountant(accountant) is accountant

    for role in (UserRole.USER, UserRole.APPROVER, UserRole.RRHH):
        with pytest.raises(HTTPException) as error:
            require_accountant(User("oid", "user@example.com", "User", role=role))
        assert error.value.status_code == status.HTTP_403_FORBIDDEN
