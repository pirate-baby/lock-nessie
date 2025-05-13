from keycloak import KeycloakOpenID
from common.logger import get_logger
from server.settings import settings

logger = get_logger(__name__)


class KeycloakAuth:

    def __init__(self):

        self.keycloak_app = KeycloakOpenID(
            server_url=settings.openid_url,
            client_id=settings.openid_client_id,
            realm_name=settings.openid_realm,
            client_secret_key=settings.openid_client_secret,
        )

    def get_auth_url(self) -> str:
        return self.keycloak_app.auth_url(
            scope="User.Read",
            redirect_url=self.redirect_uri
        )

    def exchange_code_for_token(self, code: str) -> str:
        self.logger.info("Exchanging code for tokens")
        return self.keycloak_app.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self.redirect_uri,
        )
