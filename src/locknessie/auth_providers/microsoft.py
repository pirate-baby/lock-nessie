from typing import TYPE_CHECKING, Optional, TYPE_CHECKING
import msal
from locknessie.logger import get_logger
from locknessie.auth_providers.base import AuthBase, AuthType

if TYPE_CHECKING:
    from pathlib import Path
    from locknessie.settings import ConfigSettings

logger = get_logger(__name__)

class MicrosoftAuth(AuthBase):
    scopes: list[str]
    cache_file_name: str = "microsoft/cache.bin"
    cache_file: "Path"
    account: "msal.Account"
    app: "msal.PublicClientApplication"
    cache: "msal.SerializableTokenCache"

    def __init__(self,
                 settings: "ConfigSettings",
                 auth_type: Optional[AuthType] = AuthType.user):
        """
        auth_type: the type of authentication to use - users can log in with a browser, daemons can use secret credentials.
        """
        super().__init__(settings=settings, auth_type=auth_type)
        self.cache = None
        if self.auth_type == AuthType.user:
            self.scopes = ["User.Read"]
            self.cache_file = self.initilaize_cache_file(self.cache_file_name)
            self.cache = self._load_cache(self.cache_file)
        elif self.auth_type == AuthType.daemon:
            self.scopes = ["https://graph.microsoft.com/.default"]
            assert settings.openid_secret, "OpenID secret is required for daemon auth"
        else:
            raise ValueError(f"Invalid auth type: {self.auth_type}")

        self.app = self._get_app(self.cache)
        self.account = self._get_client_id_account(self.app)


    def get_token(self) -> str:
        return self._get_token()

    def initilaize_cache_file(self, cache_file_name: str) -> "Path":
        cache_file = self.settings.config_dir / cache_file_name
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        return cache_file

    def _load_cache(self, cache_file: "Path") -> msal.SerializableTokenCache:
        logger.info("initializing auth cache...")
        cache = msal.SerializableTokenCache()
        if cache_file.exists():
            logger.info("loading auth cache from %s", cache_file)
            cache.deserialize(cache_file.read_text())
            logger.info("auth cache loaded")
        logger.info("auth cache initialized")
        return cache

    def _get_app(self, cache: Optional["msal.SerializableTokenCache"] = None) -> "msal.PublicClientApplication":
        match self.auth_type:
            case AuthType.daemon:
                return msal.ConfidentialClientApplication(
                    client_id=self.settings.openid_client_id,
                    client_credential=self.settings.openid_secret,
                    authority=f"https://login.microsoftonline.com/{self.settings.openid_tenant}"
                )
            case AuthType.user:
                extra_args = {}
                if not self.settings.openid_allow_all_tenants:
                    extra_args["authority"] = f"https://login.microsoftonline.com/{self.settings.openid_tenant}"
                return msal.PublicClientApplication(client_id=self.settings.openid_client_id,
                                                    token_cache=cache,
                                                    **extra_args)
            case _:
                raise ValueError(f"Invalid auth type: {self.auth_type}")

    def _get_client_id_account(self, app: "msal.PublicClientApplication") -> "msal.Account":
        """get the first selected account. Note that browser auth needs to succeed first."""
        try:
            return app.get_accounts()[0]
        except IndexError:
            return None

    def _get_token(self) -> str:
        match self.auth_type:
            case AuthType.user:
                return self._get_user_token()
            case AuthType.daemon:
                return self._get_daemon_token()
            case _:
                raise ValueError(f"Invalid auth type: {self.auth_type}")

    def _get_daemon_token(self) -> str:
        logger.info("getting daemon token...")
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        return self._extract_token_from_result(result)

    def _get_user_token(self) -> str:
        logger.info("getting user token...")
        logger.info("attempting to get token silently with refresh...")
        if not self.account or \
            not (result := self.app.acquire_token_silent(scopes=self.scopes, account=self.account)):
            logger.info("no token or account found, attempting to get token interactively via browser...")
            result = self.app.acquire_token_interactive(scopes=self.scopes, port=1234)
        token = self._extract_token_from_result(result)
        self._save_cache(self.cache_file, self.cache)
        return token

    def _extract_token_from_result(self, result: dict) -> str:
        if "access_token" in result:
            logger.info("token acquired")
            return result["access_token"]
        msg = result.get("error_description", "Authentication failed with an unknown error")
        raise ValueError(msg)

    def _save_cache(self, cache_file: "Path", cache: "msal.SerializableTokenCache"):
        cache_file.write_text(cache.serialize())


