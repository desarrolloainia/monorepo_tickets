from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    tenant_id: str = Field(validation_alias="MICROSOFT_TENANT_ID")
    client_id: str = Field(validation_alias="MICROSOFT_CLIENT_ID")
    client_secret: str = Field(validation_alias="MICROSOFT_CLIENT_SECRET")
    redirect_uri: str = Field(validation_alias="MICROSOFT_REDIRECT_URI")
    cookie_secret: str = Field(min_length=1, validation_alias="AUTH_COOKIE_SECRET")
    success_redirect_url: str = Field(validation_alias="AUTH_SUCCESS_REDIRECT_URL")
    cookie_secure: bool = Field(default=True, validation_alias="AUTH_COOKIE_SECURE")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def authority(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}"


auth_settings = AuthSettings()  # pyright: ignore[reportCallIssue]

ACCESS_TOKEN_COOKIE = "access_token"
OAUTH_STATE_COOKIE = "oauth_state"
ACCESS_TOKEN_TTL_SECONDS = 3600
OAUTH_STATE_TTL_SECONDS = 600
JWT_ISSUER = "tickets-api"
JWT_AUDIENCE = "tickets-web"
