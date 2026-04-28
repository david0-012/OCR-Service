import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> logging.Logger:
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        logging.WARNING
    )

    logger = logging.getLogger(settings.APP_NAME)
    logger.info(f"Logging configurado | nivel={'DEBUG' if settings.DEBUG else 'INFO'}")
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)