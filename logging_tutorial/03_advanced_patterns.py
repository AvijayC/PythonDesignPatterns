#!/usr/bin/env python3
"""
Advanced Logging Patterns for Production Code
"""

import logging
import logging.config
import json
from pathlib import Path
from datetime import datetime
import functools
import time

# Pattern 1: Dictionary Configuration (Recommended)
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
        },
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'critical_module': {  # Specific module logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Apply configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Pattern 2: Context Manager for Timed Operations
class LoggedTimer:
    """Context manager that logs execution time"""
    def __init__(self, logger, operation_name, level=logging.INFO):
        self.logger = logger
        self.operation_name = operation_name
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log(self.level, f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if exc_type:
            self.logger.error(
                f"Failed: {self.operation_name} after {elapsed:.2f}s - {exc_val}"
            )
        else:
            self.logger.log(
                self.level, 
                f"Completed: {self.operation_name} in {elapsed:.2f}s"
            )

# Pattern 3: Decorator for Automatic Function Logging
def log_function_call(logger=None, level=logging.DEBUG):
    """Decorator that logs function calls with arguments and results"""
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log the call
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.log(level, f"Calling {func.__name__}({signature})")
            
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"{func.__name__} returned {result!r}")
                return result
            except Exception as e:
                logger.exception(f"{func.__name__} raised {e.__class__.__name__}")
                raise
        
        return wrapper
    return decorator

# Pattern 4: Structured Logging with Extra Context
class StructuredLogger:
    """Logger that adds structured context to all messages"""
    def __init__(self, name, **default_context):
        self.logger = logging.getLogger(name)
        self.default_context = default_context
    
    def _log(self, level, msg, **extra_context):
        context = {**self.default_context, **extra_context}
        # Create JSON-like structured message
        structured_msg = {
            'message': msg,
            'timestamp': datetime.utcnow().isoformat(),
            **context
        }
        self.logger.log(level, json.dumps(structured_msg))
    
    def info(self, msg, **kwargs):
        self._log(logging.INFO, msg, **kwargs)
    
    def error(self, msg, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)
    
    def debug(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

# Pattern 5: Performance Logging
class PerformanceLogger:
    """Track and log performance metrics"""
    def __init__(self, logger):
        self.logger = logger
        self.metrics = {}
    
    def record_metric(self, name, value, unit='ms'):
        """Record a performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        
        # Log if value is unusual
        if self.metrics[name]:
            avg = sum(self.metrics[name]) / len(self.metrics[name])
            if value > avg * 2:  # More than 2x average
                self.logger.warning(
                    f"Performance degradation: {name} = {value}{unit} "
                    f"(avg: {avg:.2f}{unit})"
                )

# Example usage
def demo_advanced_patterns():
    # Get loggers
    logger = logging.getLogger(__name__)
    critical_logger = logging.getLogger('critical_module')
    
    # 1. Using timer context manager
    with LoggedTimer(logger, "Database Query"):
        time.sleep(0.1)  # Simulate work
    
    # 2. Using function decorator
    @log_function_call(logger=logger)
    def calculate_something(x, y, operation='add'):
        if operation == 'add':
            return x + y
        elif operation == 'multiply':
            return x * y
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    result = calculate_something(5, 3, operation='multiply')
    
    # 3. Structured logging
    struct_logger = StructuredLogger(
        'api_requests',
        service='marketing_platform',
        environment='production'
    )
    struct_logger.info(
        "API request processed",
        endpoint='/api/v1/data',
        method='GET',
        status_code=200,
        response_time_ms=145
    )
    
    # 4. Performance tracking
    perf_logger = PerformanceLogger(logger)
    for i in range(5):
        # Simulate varying response times
        response_time = 100 + (i * 50)
        perf_logger.record_metric('api_response_time', response_time)
    
    critical_logger.error("This goes to error file too!")

if __name__ == "__main__":
    demo_advanced_patterns()
    print("\nCheck log files: app.log and errors.log")