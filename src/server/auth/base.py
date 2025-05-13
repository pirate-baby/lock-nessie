from typing import TYPE_CHECKING, Optional
from common.logger import get_logger
from server.settings import settings

if TYPE_CHECKING:
    from logging import Logger

class AuthBase:
    logger: "Logger"
    redirect_uri: str

    def __init__(self, redirect_uri: Optional[str]=None):
        self.logger = get_logger(self.__class__.__name__)
        self.redirect_uri = redirect_uri or f"{settings.redirect_base}/auth/callback"
