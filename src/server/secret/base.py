from abc import ABC, abstractmethod
import re
from common.logger import get_logger
from server.settings import settings

class SecretBase(ABC):
    user: str
    secret_name: str
    logger: "Logger"
    deleted_string:str = "DELETED"

    def __init__(self, user: str):
        self.logger = get_logger(self.__class__.__name__)
        self.user = user
        self.secret_name = self.build_secret_name(user)

    def build_secret_name(self, user: str):
        """build the secret name from the user"""
        safe_user = re.sub(r"[^a-zA-Z0-9]", "-", user).strip("-")
        return f"{settings.openid_client_id}-{safe_user}"

    @abstractmethod
    def set_token_value(self, secret: str):
        """set the token value in the secret store"""

    @abstractmethod
    def delete_token_value(self):
        """delete the token value from the secret store"""