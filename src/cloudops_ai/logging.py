"""Structured logging — JSON to stdout + rotating file."""

import logging
import logging.handlers
import sys
from pathlib import Path

import structlog

LOG_DIR = Path("/home/ubuntu/cloudops-ai/logs")
LOG_FILE = LOG_DIR / "cloudops-ai.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


class _TeeStream:
    """Write to both stdout and a rotating file atomically."""

    def __init__(self, file_handler: logging.handlers.RotatingFileHandler) -> None:
        self._fh = file_handler

    def write(self, msg: str) -> None:
        sys.stdout.write(msg)
        if msg.strip():
            record = logging.makeLogRecord({"msg": msg.rstrip()})
            self._fh.emit(record)

    def flush(self) -> None:
        sys.stdout.flush()
        self._fh.flush()


def configure_logging(log_level: str = "INFO") -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_level.upper(), logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    tee = _TeeStream(file_handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=tee),  # type: ignore[arg-type]
    )
