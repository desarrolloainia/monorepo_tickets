import json
from dataclasses import dataclass
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import msal

from modules.auth.config import auth_settings


class MicrosoftGraphError(Exception):
    pass


class MicrosoftUserNotFound(MicrosoftGraphError):
    pass


@dataclass(frozen=True)
class MicrosoftDirectoryUser:
    microsoft_oid: str
    email: str | None
    name: str


class MicrosoftGraph:
    def _token(self) -> str:
        # ponytail: RRHH traffic is low; share a token cache only if Graph usage grows.
        result = msal.ConfidentialClientApplication(
            auth_settings.client_id,
            client_credential=auth_settings.client_secret,
            authority=auth_settings.authority,
        ).acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if not isinstance(result, dict):
            raise MicrosoftGraphError("Microsoft Graph no devolvió un token de acceso")
        token = result.get("access_token")
        if not isinstance(token, str):
            raise MicrosoftGraphError("Microsoft Graph no devolvió un token de acceso")
        return token

    def _get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"https://graph.microsoft.com/v1.0/{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token()}",
                "ConsistencyLevel": "eventual",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read())
        except HTTPError as exc:
            if exc.code == 404:
                raise MicrosoftUserNotFound from exc
            raise MicrosoftGraphError from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise MicrosoftGraphError from exc
        if not isinstance(payload, dict):
            raise MicrosoftGraphError("Respuesta inválida de Microsoft Graph")
        return cast(dict[str, Any], payload)

    @staticmethod
    def _user(data: dict[str, Any]) -> MicrosoftDirectoryUser:
        microsoft_oid = data.get("id")
        email = data.get("mail") or data.get("userPrincipalName")
        name = data.get("displayName") or email or microsoft_oid
        if not isinstance(microsoft_oid, str) or not isinstance(name, str):
            raise MicrosoftGraphError("Usuario inválido en Microsoft Graph")
        return MicrosoftDirectoryUser(
            microsoft_oid,
            email if isinstance(email, str) else None,
            name,
        )

    def search_users(self, query: str) -> list[MicrosoftDirectoryUser]:
        escaped = query.replace("\\", "\\\\").replace('"', '\\"')
        payload = self._get(
            "users",
            {
                "$search": (
                    f'"displayName:{escaped}" OR "mail:{escaped}" '
                    f'OR "userPrincipalName:{escaped}"'
                ),
                "$select": "id,displayName,mail,userPrincipalName",
                "$top": "20",
            },
        )
        values = payload.get("value")
        if not isinstance(values, list):
            raise MicrosoftGraphError("Respuesta inválida de Microsoft Graph")
        return [self._user(value) for value in values if isinstance(value, dict)]

    def get_user(self, microsoft_oid: str) -> MicrosoftDirectoryUser:
        return self._user(
            self._get(
                f"users/{quote(microsoft_oid, safe='')}",
                {"$select": "id,displayName,mail,userPrincipalName"},
            )
        )


microsoft_graph = MicrosoftGraph()
