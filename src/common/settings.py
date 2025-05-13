from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class SecretProvider(str, Enum):
    aws_secrets_manager = "aws_secrets_manager"

class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="locknessie_", case_sensitive=False)

    deleted_string: str = Field("DELETED", description="The string to use when the secret is deleted")