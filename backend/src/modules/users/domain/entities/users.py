from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class UserRole(StrEnum):
    USER = "user"
    APPROVER = "approver"
    RRHH = "rrhh"
    ACCOUNTANT = "accountant"


@dataclass
class User:
    microsoft_oid: str
    email: str
    name: str
    role: UserRole = UserRole.USER
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class BlockedUser:
    microsoft_oid: str
    email: str | None
    name: str
    blocked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
