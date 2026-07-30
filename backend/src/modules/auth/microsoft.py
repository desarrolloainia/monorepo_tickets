from typing import Any

import msal

from modules.auth.config import auth_settings


class MicrosoftOAuth:
    def _client(self) -> msal.ConfidentialClientApplication:
        return msal.ConfidentialClientApplication(
            auth_settings.client_id,
            client_credential=auth_settings.client_secret,
            authority=auth_settings.authority,
        )

    def authorization_url(self, state: str) -> str:
        return self._client().get_authorization_request_url(
            scopes=["email"],
            state=state,
            redirect_uri=auth_settings.redirect_uri,
        )

    def exchange_code(self, code: str) -> dict[str, Any]:
        result = self._client().acquire_token_by_authorization_code(
            code,
            scopes=["email"],
            redirect_uri=auth_settings.redirect_uri,
        )
        if result.get("error"):
            raise ValueError(str(result.get("error_description") or result["error"]))
        claims = result.get("id_token_claims")
        if not isinstance(claims, dict) or not claims:
            raise ValueError("Microsoft no devolvió id_token_claims")
        return claims


microsoft_oauth = MicrosoftOAuth()
