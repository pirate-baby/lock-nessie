from typing import Optional
from pathlib import Path
from pydantic import Field
from enum import Enum
from common.settings import CommonSettings, SecretProvider

class Settings(CommonSettings):

    # Redirect base
    server_url: Optional[str] = Field(None, description="The base URL for the server. If set, the client will open a login window when the token is expired.")

    # Secret settings
    secret_provider: SecretProvider = Field(..., description="The provider where the secret is stored")
    secret_identifier: str = Field(..., description="The identifier for the secret")
    secret_cache_path: Optional[Path] = Field(Path.home() / ".locknessie" / "token", description="The path to where the token cache is stored")

settings = Settings()