from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.domain.entities.users import User, UserRole
from modules.users.infrastructure.sqlalchemy.persistence.models import UserModel


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            microsoft_oid=model.microsoft_oid,
            email=model.email,
            name=model.name,
            role=UserRole(model.role),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            microsoft_oid=user.microsoft_oid,
            email=user.email,
            name=user.name,
            role=str(user.role),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def add(self, user: User) -> None:
        self.session.add(self._to_model(user))
        await self.session.flush()

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self.session.get(UserModel, user_id)
        return None if model is None else self._to_entity(model)

    async def get_by_microsoft_oid(self, microsoft_oid: str) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.microsoft_oid == microsoft_oid)
        )
        return None if model is None else self._to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        model = await self.session.scalar(select(UserModel).where(UserModel.email == email))
        return None if model is None else self._to_entity(model)

    async def list_all(self) -> list[User]:
        models = await self.session.scalars(select(UserModel))
        return [self._to_entity(model) for model in models]

    async def update(self, user: User) -> None:
        _ = await self.session.merge(self._to_model(user))
        await self.session.flush()

    async def delete(self, user_id: UUID) -> None:
        _ = await self.session.execute(delete(UserModel).where(UserModel.id == user_id))
