from typing import TYPE_CHECKING
from locknessie.settings import safely_get_settings, OpenIDIssuer
from typing import Optional
from locknessie.auth_providers.base import AuthType

if TYPE_CHECKING:
    from locknessie.settings import ConfigSettings

class LockNessie:
    settings: "ConfigSettings"

    def __init__(self, auth_type: Optional[str] = AuthType.user, **kwargs):
        """set the correct provider based on the settings"""
        self.settings = safely_get_settings(**kwargs)
        self.provider = self._get_provider(auth_type=auth_type)

    def _get_provider(self, auth_type: str) -> str:
        """returns the correct provider based on the settings"""
        match self.settings.openid_issuer:
            case OpenIDIssuer.microsoft:
                from locknessie.auth_providers.microsoft import MicrosoftAuth
                return MicrosoftAuth(auth_type=auth_type, settings=self.settings)
            case _:
                raise NotImplementedError("Not implemented")

    def get_token(self) -> str:
        """returns the authed/updated bearer token to be used for the OpenID connection"""
        return self.provider.get_token()