from typing import TYPE_CHECKING
import msal
from locknessie.logger import get_logger
from locknessie.settings import safely_get_settings

if TYPE_CHECKING:
    from pathlib import Path

settings = safely_get_settings()

logger = get_logger(__name__)

class MicrosoftAuth:

    scopes: list[str] = ["User.Read"]
    cache_file_name: str = "microsoft/cache.bin"
    cache_file: "Path"
    account: "msal.Account"
    app: "msal.PublicClientApplication"
    cache: "msal.SerializableTokenCache"

    def __init__(self):
        self.cache_file = self.initilaize_cache_file(self.cache_file_name)
        self.cache = self._load_cache(self.cache_file)
        self.app = self._get_app(self.cache)
        self.account = self._get_client_id_account(self.app)

    def initilaize_cache_file(self, cache_file_name: str) -> "Path":
        cache_file = settings.env.config_path / cache_file_name
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

    def _get_app(self, cache: "msal.SerializableTokenCache") -> "msal.PublicClientApplication":
        return msal.PublicClientApplication(client_id=settings.openid_client_id,
                                            token_cache=cache)

    def _get_client_id_account(self, app: "msal.PublicClientApplication") -> "msal.Account":
        """get the first selected account. Note that browser auth needs to succeed first."""
        try:
            return app.get_accounts()[0]
        except IndexError:
            return None

    def get_token(self) -> str:
        logger.info("getting token...")
        logger.info("attempting to get token silently with refresh...")
        if not self.account or \
            not (result := self.app.acquire_token_silent(scopes=self.scopes, account=self.account)):
            logger.info("no token or account found, attempting to get token interactively via browser...")
            result = self.app.acquire_token_interactive(scopes=self.scopes, port=1234)
        if "access_token" in result:
            logger.info("token acquired")
            self._save_cache(self.cache_file, self.cache)
            return result["access_token"]
        msg = result.get("error_description", "Authentication failed with an unknown error")
        raise ValueError(msg)

    def _save_cache(self, cache_file: "Path", cache: "msal.SerializableTokenCache"):
        cache_file.write_text(cache.serialize())


