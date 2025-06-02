from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class AuthType(str, Enum):
    user = "user"
    daemon = "daemon"


class AuthBase(ABC):
    _auth_type: AuthType

    def __init__(self, auth_type: Optional[AuthType] = AuthType.user):
        self._auth_type = auth_type

    @property
    def auth_type(self) -> AuthType:
        return self._auth_type

    @abstractmethod
    def get_token(self) -> str:
        pass