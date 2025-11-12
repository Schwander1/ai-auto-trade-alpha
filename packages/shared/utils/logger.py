"""
Structured logging utilities for Python
Provides consistent logging across Argo and Alpine backend
"""

import json
import logging
import sys
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional


class LogLevel(IntEnum):
    """Log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    ERROR = logging.ERROR


class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, name: str = "argo-alpine", level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add JSON formatter handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None):
        """Internal log method"""
        extra = context or {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **context):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, **context):
        """Log info message"""
        self._log(LogLevel.INFO, message, context)
    
    def warn(self, message: str, **context):
        """Log warning message"""
        self._log(LogLevel.WARN, message, context)
    
    def error(self, message: str, **context):
        """Log error message"""
        self._log(LogLevel.ERROR, message, context)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra context
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Create default logger instance
logger = StructuredLogger()

# Export convenience functions
def debug(message: str, **context):
    """Log debug message"""
    logger.debug(message, **context)


def info(message: str, **context):
    """Log info message"""
    logger.info(message, **context)


def warn(message: str, **context):
    """Log warning message"""
    logger.warn(message, **context)


def error(message: str, **context):
    """Log error message"""
    logger.error(message, **context)

