import logging
import sys
from .config import Settings

class LoggingManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    def setup_logging(self):
        """Configure application-wide logging for the Home Assistant environment."""
        log_format = "[%(module)-18s] %(message)s"
        app_formatter = logging.Formatter(log_format)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(app_formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(self.settings.LOG_LEVEL)
        
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
        root_logger.addHandler(handler)

    def get_uvicorn_log_config(self) -> dict:
        """Generate a logging configuration dictionary for Uvicorn."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"()": "logging.Formatter", "fmt": "[%(name)-18s] %(message)s"},
                "access": {"()": "logging.Formatter", "fmt": "[%(name)-18s] %(message)s"},
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
        }

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name."""
    return logging.getLogger(name)
