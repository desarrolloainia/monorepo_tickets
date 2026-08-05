from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from modules.users.domain.entities.users import UserRole


class UserDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: UserRole


class UserRoleUpdateDTO(BaseModel):
    role: UserRole


class MicrosoftUserDTO(BaseModel):
    microsoft_oid: str
    email: str | None
    name: str
    blocked: bool


class BlockedUserDTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    microsoft_oid: str
    email: str | None
    name: str
    blocked_at: datetime
