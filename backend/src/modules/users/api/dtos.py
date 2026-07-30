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
