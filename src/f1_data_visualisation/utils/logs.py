import logging
import sys

import structlog


# Configure JSON logging.
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
        structlog.processors.JSONRenderer(sort_keys=True),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

_event_logger = structlog.get_logger("events")
_error_logger = structlog.get_logger("errors")


def log_event(event_type: str, **params: str | int | float) -> None:
    """
    Log an application event with structured parameters.

    The event type should look something like "category.event.status".
    """
    _event_logger.info(event_type, **params)


def error(message: str) -> None:
    """
    Log an application error.

    This is intended to be called from within an try/except block so it can capture the stack
    trace.
    """
    _error_logger.exception("application.error", message=message)
