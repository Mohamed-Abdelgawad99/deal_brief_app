import os, sys
from loguru import logger


def get_logger():
    logger.remove()  # Remove default logger
    
    custom_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<magenta>{file}</magenta>:<red>{line}</red> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=custom_format,
        level=os.getenv("LOGGING_LEVEL", "DEBUG").upper(),
    )

    return logger

logger = get_logger()