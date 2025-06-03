from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from locknessie.settings import ConfigSettings

class AuthType(str, Enum):
    user = "user"
    daemon = "daemon"


class AuthBase(ABC):
    _auth_type: AuthType
    settings: "ConfigSettings"

    def __init__(self,
                 settings: "ConfigSettings",
                 auth_type: Optional[AuthType] = AuthType.user):
        self._auth_type = auth_type
        self.settings = settings

    @property
    def auth_type(self) -> AuthType:
        return self._auth_type

    @abstractmethod
    def get_token(self) -> str:
        pass