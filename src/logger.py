from logging import getLogger, Logger

base_logger = getLogger("lock-nessie")
def get_logger(name: str) -> "Logger":
    return base_logger.getChild(name)