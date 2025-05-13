from msal import ConfidentialClientApplication
from common.logger import get_logger
from server.settings import settings
from server.auth.base import AuthBase

logger = get_logger(__name__)


class MicrosoftAuth(AuthBase):

    def __init__(self):
        super().__init__()
        self.authority = f"https://login.microsoftonline.com/{settings.openid_tenant}"
        logger.info(f"Initializing MSAL with authority: {self.authority}")
        logger.info(f"Client ID length: {len(settings.openid_client_id)}")

        self.msal_app = ConfidentialClientApplication(
            client_id=settings.openid_client_id,
            client_credential=settings.openid_client_secret,
            authority=self.authority,
        )

    def get_auth_url(self) -> str:
        return self.msal_app.get_authorization_request_url(
            scopes=["User.Read"], redirect_uri=self.redirect_uri, response_type="code"
        )

    def exchange_code_for_token(self, code: str) -> str:
        self.logger.info("Exchanging code for tokens")
        return self.msal_app.acquire_token_by_authorization_code(
            code=code,
            scopes=["User.Read"],
            redirect_uri=self.redirect_uri,
        )
