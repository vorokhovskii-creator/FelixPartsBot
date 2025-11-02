"""
Structured logging utilities with correlation ID support.
"""
import logging
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Optional

# Context variable to store correlation ID per request
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

logger = logging.getLogger(__name__)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in context."""
    correlation_id_ctx.set(correlation_id)


class StructuredLogger:
    """Logger wrapper that adds correlation IDs and structured context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _format_message(self, message: str, **context) -> str:
        """Format message with correlation ID and context."""
        correlation_id = get_correlation_id()
        
        parts = []
        if correlation_id:
            parts.append(f"[requestId={correlation_id}]")
        
        # Add context fields
        context_parts = []
        for key, value in sorted(context.items()):
            if value is not None:
                context_parts.append(f"{key}={value}")
        
        if context_parts:
            parts.append(f"[{', '.join(context_parts)}]")
        
        parts.append(message)
        return " ".join(parts)
    
    def debug(self, message: str, **context):
        """Log debug message with context."""
        self.logger.debug(self._format_message(message, **context))
    
    def info(self, message: str, **context):
        """Log info message with context."""
        self.logger.info(self._format_message(message, **context))
    
    def warning(self, message: str, **context):
        """Log warning message with context."""
        self.logger.warning(self._format_message(message, **context))
    
    def error(self, message: str, **context):
        """Log error message with context."""
        self.logger.error(self._format_message(message, **context))
    
    def critical(self, message: str, **context):
        """Log critical message with context."""
        self.logger.critical(self._format_message(message, **context))


def with_correlation_id(func):
    """
    Decorator to automatically generate and set correlation ID for a function.
    Useful for API endpoints.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate or reuse correlation ID
        correlation_id = get_correlation_id()
        if not correlation_id:
            correlation_id = generate_correlation_id()
            set_correlation_id(correlation_id)
        
        try:
            return func(*args, **kwargs)
        finally:
            # Clear correlation ID after request
            correlation_id_ctx.set(None)
    
    return wrapper


def log_operation(operation_name: str, **context):
    """
    Decorator to log start and end of an operation with timing.
    
    Usage:
        @log_operation("order_creation", order_id=order.id)
        def create_order():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            slogger = StructuredLogger(func.__module__)
            start_time = time.time()
            
            slogger.info(f"Starting {operation_name}", **context)
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                slogger.info(
                    f"Completed {operation_name}",
                    duration_ms=int(elapsed * 1000),
                    **context
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                slogger.error(
                    f"Failed {operation_name}: {str(e)}",
                    duration_ms=int(elapsed * 1000),
                    error_type=type(e).__name__,
                    **context
                )
                raise
        
        return wrapper
    return decorator
