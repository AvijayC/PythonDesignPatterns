#!/usr/bin/env python3
"""
Error Handling Patterns: Comprehensive Strategies
"""

import logging
import functools
import time
from typing import Optional, Union, Callable, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================================================================
# PATTERN 1: Result Type (Rust-inspired)
# ==================================================================

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result type that explicitly handles success/failure"""
    
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        assert (value is None) != (error is None), "Result must have either value or error"
        self._value = value
        self._error = error
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        """Create successful result"""
        return cls(value=value)
    
    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        """Create error result"""
        return cls(error=error)
    
    def is_ok(self) -> bool:
        return self._value is not None
    
    def is_err(self) -> bool:
        return self._error is not None
    
    def unwrap(self) -> T:
        """Get value or raise exception"""
        if self._error:
            raise ValueError(f"Called unwrap on error: {self._error}")
        return self._value
    
    def unwrap_or(self, default: T) -> T:
        """Get value or return default"""
        return self._value if self.is_ok() else default
    
    def map(self, func: Callable[[T], Any]) -> 'Result':
        """Transform value if ok"""
        if self.is_ok():
            try:
                return Result.ok(func(self._value))
            except Exception as e:
                return Result.err(e)
        return self

# Example: Using Result type
def divide_safe(a: float, b: float) -> Result[float, str]:
    """Division that returns Result instead of raising exception"""
    if b == 0:
        return Result.err("Division by zero")
    return Result.ok(a / b)

def process_calculation() -> Result[float, str]:
    """Chain operations with Result"""
    result = divide_safe(10, 2)
    
    if result.is_ok():
        # Chain another operation
        return divide_safe(result.unwrap(), 0.5)
    
    return result

# ==================================================================
# PATTERN 2: Retry with Exponential Backoff
# ==================================================================

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for automatic retry with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            delay = base_delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
                    attempt += 1
            
            raise RuntimeError(f"Failed after {max_attempts} attempts")
        
        return wrapper
    return decorator

# Example: Retrying network operations
@retry_with_backoff(max_attempts=3, base_delay=1.0)
def fetch_data_from_api(url: str) -> dict:
    """Simulated API call with retry"""
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("Network timeout")
    return {"data": "success"}

# ==================================================================
# PATTERN 3: Circuit Breaker
# ==================================================================

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")

# ==================================================================
# PATTERN 4: Fallback/Default Values
# ==================================================================

class FallbackHandler:
    """Provides fallback values for failed operations"""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable):
        """Try primary function, use fallback on failure"""
        def wrapper(*args, **kwargs):
            try:
                return primary_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Primary function failed: {e}. Using fallback.")
                return fallback_func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def with_default(default_value: Any):
        """Decorator that returns default value on exception"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"{func.__name__} failed: {e}. Returning default.")
                    return default_value
            return wrapper
        return decorator

# Example: Fallback patterns
@FallbackHandler.with_default(default_value={})
def load_config(filepath: str) -> dict:
    """Load config with fallback to empty dict"""
    with open(filepath) as f:
        import json
        return json.load(f)

def get_from_cache(key: str) -> Optional[str]:
    """Get from cache (might fail)"""
    raise ConnectionError("Cache unavailable")

def get_from_database(key: str) -> str:
    """Get from database (fallback)"""
    return f"db_value_for_{key}"

# Use fallback
get_value = FallbackHandler.with_fallback(get_from_cache, get_from_database)

# ==================================================================
# PATTERN 5: Error Aggregation
# ==================================================================

class ErrorCollector:
    """Collect errors without stopping execution"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: Exception, context: str = None):
        """Add error with optional context"""
        self.errors.append({
            'error': error,
            'context': context,
            'traceback': traceback.format_exc()
        })
    
    def add_warning(self, message: str, context: str = None):
        """Add warning message"""
        self.warnings.append({
            'message': message,
            'context': context
        })
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def raise_if_errors(self):
        """Raise exception if any errors collected"""
        if self.has_errors():
            error_messages = [f"{e['context']}: {e['error']}" for e in self.errors]
            raise RuntimeError(f"Collected {len(self.errors)} errors: {error_messages}")
    
    def get_summary(self) -> dict:
        """Get summary of all collected issues"""
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }

# Example: Batch processing with error collection
def process_batch_with_collection(items: list) -> ErrorCollector:
    """Process items, collecting errors instead of failing"""
    collector = ErrorCollector()
    results = []
    
    for i, item in enumerate(items):
        try:
            # Process item (might fail)
            if item < 0:
                raise ValueError(f"Negative value: {item}")
            results.append(item * 2)
        except Exception as e:
            collector.add_error(e, f"Item {i}")
    
    # Add warning if too many errors
    if collector.has_errors() and len(collector.errors) > len(items) * 0.1:
        collector.add_warning("More than 10% of items failed", "batch_processing")
    
    return collector

# ==================================================================
# PATTERN 6: Context Managers for Cleanup
# ==================================================================

@contextmanager
def error_handler(operation_name: str, cleanup_func: Callable = None):
    """Context manager for consistent error handling and cleanup"""
    logger.info(f"Starting: {operation_name}")
    start_time = time.time()
    
    try:
        yield
        elapsed = time.time() - start_time
        logger.info(f"Completed: {operation_name} in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Failed: {operation_name} after {elapsed:.2f}s - {e}")
        
        if cleanup_func:
            logger.info(f"Running cleanup for {operation_name}")
            try:
                cleanup_func()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")
        
        raise
    finally:
        logger.debug(f"Finalizing: {operation_name}")

# Example usage
def cleanup_temp_files():
    """Cleanup function"""
    print("Cleaning up temporary files...")

# ==================================================================
# PATTERN 7: Graceful Degradation
# ==================================================================

class FeatureFlags:
    """Feature flags for graceful degradation"""
    
    def __init__(self):
        self.flags = {
            'use_cache': True,
            'enable_analytics': True,
            'use_ml_model': True
        }
        self.degraded_features = set()
    
    def degrade_feature(self, feature: str, reason: str):
        """Mark feature as degraded"""
        self.flags[feature] = False
        self.degraded_features.add(feature)
        logger.warning(f"Feature '{feature}' degraded: {reason}")
    
    def is_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.flags.get(feature, False)
    
    def with_degradation(self, feature: str, primary_func: Callable, 
                        degraded_func: Callable):
        """Execute with automatic degradation"""
        def wrapper(*args, **kwargs):
            if self.is_enabled(feature):
                try:
                    return primary_func(*args, **kwargs)
                except Exception as e:
                    self.degrade_feature(feature, str(e))
                    return degraded_func(*args, **kwargs)
            else:
                return degraded_func(*args, **kwargs)
        return wrapper

# ==================================================================
# PATTERN 8: Error Recovery Strategies  
# ==================================================================

class RecoveryStrategy(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    FAIL = "fail"

@dataclass
class ErrorRecoveryConfig:
    """Configuration for error recovery"""
    strategy: RecoveryStrategy
    max_retries: int = 3
    fallback_value: Any = None
    should_log: bool = True

class SmartErrorHandler:
    """Intelligent error handling with multiple strategies"""
    
    def __init__(self, default_config: ErrorRecoveryConfig):
        self.default_config = default_config
        self.error_counts = {}
    
    def handle(self, func: Callable, config: Optional[ErrorRecoveryConfig] = None):
        """Handle function execution with configured strategy"""
        config = config or self.default_config
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            if config.strategy == RecoveryStrategy.RETRY:
                for attempt in range(config.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == config.max_retries - 1:
                            if config.should_log:
                                logger.error(f"{func_name} failed after {config.max_retries} attempts")
                            raise
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            elif config.strategy == RecoveryStrategy.FALLBACK:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if config.should_log:
                        logger.warning(f"{func_name} failed, using fallback")
                    return config.fallback_value
            
            elif config.strategy == RecoveryStrategy.SKIP:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if config.should_log:
                        logger.warning(f"{func_name} failed, skipping")
                    return None
            
            elif config.strategy == RecoveryStrategy.FAIL:
                return func(*args, **kwargs)  # Let it fail
            
        return wrapper

# ==================================================================
# Demo and Best Practices
# ==================================================================

def demonstrate_error_patterns():
    """Demonstrate various error handling patterns"""
    
    print("Error Handling Patterns Demo\n" + "="*50)
    
    # 1. Result Type
    print("\n1. RESULT TYPE:")
    result = divide_safe(10, 2)
    if result.is_ok():
        print(f"   Success: {result.unwrap()}")
    
    result = divide_safe(10, 0)
    if result.is_err():
        print(f"   Error handled: {result._error}")
    
    # 2. Retry with backoff
    print("\n2. RETRY WITH BACKOFF:")
    try:
        # This will retry 3 times
        # data = fetch_data_from_api("http://api.example.com")
        print("   Would retry 3 times with exponential backoff")
    except:
        pass
    
    # 3. Circuit Breaker
    print("\n3. CIRCUIT BREAKER:")
    breaker = CircuitBreaker(failure_threshold=3)
    print(f"   Initial state: {breaker.state.value}")
    
    # 4. Fallback
    print("\n4. FALLBACK PATTERN:")
    config = load_config("nonexistent.json")
    print(f"   Config with fallback: {config}")
    
    value = get_value("test_key")
    print(f"   Value from fallback: {value}")
    
    # 5. Error Collection
    print("\n5. ERROR COLLECTION:")
    items = [1, -2, 3, -4, 5]
    collector = process_batch_with_collection(items)
    summary = collector.get_summary()
    print(f"   Processed with {summary['error_count']} errors, {summary['warning_count']} warnings")
    
    # 6. Context Manager
    print("\n6. CONTEXT MANAGER:")
    try:
        with error_handler("data_processing", cleanup_temp_files):
            # Simulate work
            print("   Processing data...")
            # raise ValueError("Simulated error")  # Uncomment to see cleanup
    except:
        pass
    
    # 7. Graceful Degradation  
    print("\n7. GRACEFUL DEGRADATION:")
    features = FeatureFlags()
    
    def with_cache():
        return "cached_result"
    
    def without_cache():
        return "direct_result"
    
    get_data = features.with_degradation('use_cache', with_cache, without_cache)
    result = get_data()
    print(f"   Result: {result}")
    
    # 8. Smart Error Handler
    print("\n8. SMART ERROR HANDLER:")
    handler = SmartErrorHandler(
        ErrorRecoveryConfig(RecoveryStrategy.FALLBACK, fallback_value="default")
    )
    
    @handler.handle
    def risky_operation():
        raise ValueError("Something went wrong")
    
    result = risky_operation()
    print(f"   Handled with fallback: {result}")

if __name__ == "__main__":
    demonstrate_error_patterns()
    
    print("\n" + "="*50)
    print("Key Takeaways:")
    print("- Use Result types for explicit error handling")
    print("- Implement retry with exponential backoff for transient failures")
    print("- Circuit breakers prevent cascading failures")
    print("- Fallbacks provide graceful degradation")
    print("- Collect errors in batch processing")
    print("- Use context managers for cleanup")
    print("- Plan for graceful degradation")
    print("- Choose appropriate recovery strategies")