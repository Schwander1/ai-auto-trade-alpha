#!/usr/bin/env python3
"""
Enhanced Logging with Structured Output and Correlation IDs
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Context variable for request correlation ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)

class CorrelationIDFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id
        return True

def setup_enhanced_logging(use_json: bool = False, level: str = "INFO"):
    """Setup enhanced logging with optional JSON output"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if use_json:
        # Use structured JSON formatter
        formatter = StructuredFormatter()
    else:
        # Use readable formatter with correlation ID
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] [%(request_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationIDFilter())
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_request_id() -> Optional[str]:
    """Get current request correlation ID"""
    return request_id_var.get()

def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request correlation ID (generates new one if not provided)"""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    return request_id

def log_with_context(logger: logging.Logger, level: int, message: str, **kwargs):
    """Log with additional context fields"""
    extra = {'extra_fields': kwargs}
    logger.log(level, message, extra=extra)

