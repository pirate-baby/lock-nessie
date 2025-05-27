from locknessie.settings import safely_get_settings, OpenIDIssuer

settings = safely_get_settings()

class LockNessie:

    def __init__(self):
        """set the correct provider based on the settings"""
        self.provider = self._get_provider()

    def _get_provider(self) -> str:
        """returns the correct provider based on the settings"""
        match settings.openid_issuer:
            case OpenIDIssuer.microsoft:
                from locknessie.auth_providers.microsoft import MicrosoftAuth
                return MicrosoftAuth()
            case _:
                raise NotImplementedError("Not implemented")

    def get_token(self) -> str:
        """returns the authed/updated bearer token to be used for the OpenID connection"""
        return self.provider.get_token()