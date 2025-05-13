from typing import TYPE_CHECKING, Optional
from pyiceberg import load_catalog
from client.secret.base import get_secret_provider

if TYPE_CHECKING:
    from pyiceberg import Catalog

def load_catalog(name: Optional[str] = None, **properties: Optional[str]) -> Catalog:
    provider = get_secret_provider()
    return load_catalog(name, **properties, token=provider.token)