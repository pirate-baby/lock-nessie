from typing import Optional, Type
from abc import ABC, abstractmethod
from client.settings import settings, ExpiredAction, SecretProvider

def get_secret_provider() -> Type["SecretBase"]:
    match settings.secret_provider:
        case SecretProvider.aws_secrets_manager:
            from client.secret.aws_secrets_manager import AwsSecretsManager
            return AwsSecretsManager()
        case _:
            raise ValueError(f"Unknown secret provider: {settings.secret_provider}")

class ExpiredTokenError(Exception):
    """Exception raised when a token is expired"""

class SecretBase(ABC):
    """Base class for secret stores"""
    secret_identifier:str

    def __init__(self, secret_identifier: Optional[str] = None):
        self.secret_identifier = secret_identifier or settings.secret_identifier
        assert self.secret_identifier, "`secret_identifier` is required as either a command line argument or environment variable"

    @property
    def token(self) -> Optional[str]:
        if settings.secret_cache_path.exists():
            return settings.secret_cache_path.read_text()
        else:
            token = self.retrieve_token()
            settings.secret_cache_path.parent.mkdir(parents=True, exist_ok=True)
            settings.secret_cache_path.write_text(token, encoding="utf-8")
            return token

    @abstractmethod
    def retrieve_token(self) -> Optional[str]:
        """get the token from the secret store"""

