"""Application logging configuration for deployment environments.

Only operational metadata should be written by callers. This module configures
rotation and destinations; it does not add request, session, or data logging.
"""

from __future__ import annotations

import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def configure_application_logging(config: dict[str, Any]) -> None:
    """Configure one rotating application log without changing route behavior."""
    log_path = Path(str(config["LOG_FILE"])).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.chmod(0o700)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                },
            },
            "handlers": {
                "application_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": config["LOG_LEVEL"],
                    "formatter": "standard",
                    "filename": str(log_path),
                    "maxBytes": int(config["LOG_MAX_BYTES"]),
                    "backupCount": int(config["LOG_BACKUP_COUNT"]),
                    "encoding": "utf-8",
                },
            },
            "root": {
                "level": config["LOG_LEVEL"],
                "handlers": ["application_file"],
            },
        }
    )

    # RotatingFileHandler follows the process umask on initial creation.
    # Restrict a newly created log after configuration where the host permits it.
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            try:
                Path(handler.baseFilename).chmod(0o600)
            except OSError:
                # Logging remains available on platforms that do not expose POSIX modes.
                pass
