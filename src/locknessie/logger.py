from logging import getLogger, Logger

base_logger = getLogger("locknessie")
def get_logger(name: str) -> "Logger":
    return base_logger.getChild(name)