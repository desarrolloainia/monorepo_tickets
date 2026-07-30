from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from modules.auth.config import (
    ACCESS_TOKEN_TTL_SECONDS,
    JWT_AUDIENCE,
    JWT_ISSUER,
    auth_settings,
)
from modules.users.domain.entities.users import User


class TokenService:
    def create(self, user: User) -> str:
        now = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(user.id),
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)).timestamp()),
                "iss": JWT_ISSUER,
                "aud": JWT_AUDIENCE,
            },
            auth_settings.cookie_secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                auth_settings.cookie_secret,
                algorithms=["HS256"],
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
            )
        except InvalidTokenError as exc:
            raise ValueError("Token de sesión inválido") from exc


token_service = TokenService()
