from enum import Enum
from pydantic import Field
from typing import Optional
from common.settings import CommonSettings, SecretProvider

class OpenIDIssuer(str, Enum):
    microsoft = "microsoft"
    keycloak = "keycloak"

class Settings(CommonSettings):

    environment: str = Field(..., description="'production' for released code, 'development' for local development")

    # Redirect base
    redirect_base: str = Field(..., description="The base URL for redirects")

    # OpenID settings
    openid_issuer: OpenIDIssuer = Field(..., description="The issuer of the OpenID client")
    openid_client_id: str = Field(..., description="The client ID of the OpenID client")
    openid_client_secret: str = Field(..., description="The client secret of the OpenID client")
    openid_tenant: Optional[str] = Field(None, description="The tenant of the OpenID client")
    openid_realm: Optional[str] = Field(None, description="The realm of the OpenID client")
    openid_url: Optional[str] = Field(None, description="The URL of the OpenID provider")

    # Secret settings
    secret_provider: SecretProvider = Field(..., description="The provider where the secret is stored")

    # Cookie settings
    max_age: int = Field(default=(60 * 60 * 24 * 365), description="The maximum age of the cookie in seconds, default is 1 year")


settings = Settings()