#!/usr/bin/env python3
"""
Integrating Python Warnings with Logging
"""

import warnings
import logging
import logging.handlers
import sys
from datetime import datetime

# Set up logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('warnings_and_logs.log')
    ]
)

logger = logging.getLogger(__name__)

# Pattern 1: Capture warnings in logging system
logging.captureWarnings(True)  # This redirects all warnings to logging
warnings_logger = logging.getLogger('py.warnings')
warnings_logger.setLevel(logging.WARNING)

print("=== Pattern 1: Basic Warning Capture ===")
# Now warnings will appear in your logs
warnings.warn("This is a deprecation warning", DeprecationWarning)
warnings.warn("This is a user warning", UserWarning)

# Pattern 2: Custom Warning Categories
class PerformanceWarning(Warning):
    """Custom warning for performance issues"""
    pass

class DataQualityWarning(Warning):
    """Custom warning for data quality issues"""
    pass

class ConfigurationWarning(Warning):
    """Custom warning for configuration issues"""
    pass

# Pattern 3: Context-Aware Warning Handler
class SmartWarningHandler:
    """Handles warnings with context and converts to appropriate log levels"""
    
    def __init__(self, logger):
        self.logger = logger
        self.warning_counts = {}
        # Store original showwarning
        self.original_showwarning = warnings.showwarning
        # Replace with our handler
        warnings.showwarning = self.handle_warning
    
    def handle_warning(self, message, category, filename, lineno, file=None, line=None):
        """Custom warning handler that logs with appropriate levels"""
        # Track warning frequency
        warning_key = f"{category.__name__}:{message}"
        self.warning_counts[warning_key] = self.warning_counts.get(warning_key, 0) + 1
        
        # Format warning message
        warning_msg = f"{filename}:{lineno}: {category.__name__}: {message}"
        
        # Decide log level based on warning type and frequency
        if category == DeprecationWarning:
            self.logger.info(f"DEPRECATION: {warning_msg}")
        elif category == ResourceWarning:
            self.logger.error(f"RESOURCE ISSUE: {warning_msg}")
        elif category == PerformanceWarning:
            self.logger.warning(f"PERFORMANCE: {warning_msg}")
        elif category == DataQualityWarning:
            if self.warning_counts[warning_key] > 3:
                self.logger.error(f"DATA QUALITY (RECURRING): {warning_msg}")
            else:
                self.logger.warning(f"DATA QUALITY: {warning_msg}")
        else:
            self.logger.warning(warning_msg)
        
        # Log to file if too many warnings
        if sum(self.warning_counts.values()) > 10:
            self.logger.critical("Too many warnings generated - check system health")
    
    def get_summary(self):
        """Get summary of all warnings"""
        return dict(self.warning_counts)
    
    def reset(self):
        """Reset warning counts"""
        self.warning_counts.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original handler
        warnings.showwarning = self.original_showwarning

# Pattern 4: Warning Filters with Logging
def setup_warning_filters():
    """Configure how different warnings are handled"""
    
    # Always show DeprecationWarnings (usually hidden)
    warnings.filterwarnings('always', category=DeprecationWarning)
    
    # Ignore specific warnings
    warnings.filterwarnings('ignore', message='.*experimental.*')
    
    # Convert specific warnings to errors
    warnings.filterwarnings('error', category=DataQualityWarning)
    
    # Show only once
    warnings.filterwarnings('once', category=PerformanceWarning)

# Pattern 5: Data Validation with Warnings
class DataValidator:
    """Validates data and issues appropriate warnings/logs"""
    
    def __init__(self, logger, strict=False):
        self.logger = logger
        self.strict = strict  # If True, warnings become errors
        self.issues = []
    
    def validate_dataframe(self, df, name="dataframe"):
        """Validate a pandas-like dataframe"""
        import random  # Simulating pandas operations
        
        # Check for missing values
        missing_count = random.randint(0, 100)  # Simulated
        if missing_count > 0:
            msg = f"{name} has {missing_count} missing values"
            self.issues.append(msg)
            
            if missing_count > 50:
                if self.strict:
                    self.logger.error(msg)
                    raise DataQualityWarning(msg)
                else:
                    warnings.warn(msg, DataQualityWarning)
                    self.logger.warning(f"Data quality issue: {msg}")
            else:
                self.logger.info(f"Minor issue: {msg}")
        
        # Check for duplicates
        duplicate_count = random.randint(0, 10)  # Simulated
        if duplicate_count > 0:
            msg = f"{name} has {duplicate_count} duplicate rows"
            warnings.warn(msg, DataQualityWarning)
        
        # Check data freshness
        data_age_days = random.randint(0, 30)  # Simulated
        if data_age_days > 7:
            msg = f"{name} data is {data_age_days} days old"
            warnings.warn(msg, UserWarning)
        
        return len(self.issues) == 0

# Pattern 6: Deprecation Helper
def deprecated(reason=None, version=None, alternative=None):
    """Decorator to mark functions as deprecated"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            msg = f"Function '{func.__name__}' is deprecated"
            if version:
                msg += f" since version {version}"
            if reason:
                msg += f". Reason: {reason}"
            if alternative:
                msg += f". Use '{alternative}' instead"
            
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            logger.warning(f"Deprecated function called: {func.__name__}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage
def demo_warnings_and_logging():
    print("\n=== Pattern 2: Custom Warnings ===")
    warnings.warn("Slow query detected: 5.2 seconds", PerformanceWarning)
    warnings.warn("Missing values in column 'age'", DataQualityWarning)
    
    print("\n=== Pattern 3: Smart Warning Handler ===")
    with SmartWarningHandler(logger) as handler:
        # Generate various warnings
        for i in range(5):
            warnings.warn(f"Iteration {i} is slow", PerformanceWarning)
        
        warnings.warn("Connection pool exhausted", ResourceWarning)
        warnings.warn("Invalid config value", ConfigurationWarning)
        
        # Get summary
        print(f"Warning summary: {handler.get_summary()}")
    
    print("\n=== Pattern 5: Data Validation ===")
    validator = DataValidator(logger, strict=False)
    validator.validate_dataframe(None, "sales_data")
    
    print("\n=== Pattern 6: Deprecation ===")
    @deprecated(
        reason="Use new_process_data instead",
        version="2.0",
        alternative="new_process_data()"
    )
    def old_process_data():
        return "Processing..."
    
    result = old_process_data()
    
    # Example: Converting warnings to exceptions for testing
    print("\n=== Converting Warnings to Errors ===")
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # All warnings become errors
        try:
            warnings.warn("This will be an error", UserWarning)
        except UserWarning as e:
            logger.error(f"Warning caught as error: {e}")

# Best Practices Function
def marketing_platform_logger_setup():
    """Production-ready logger setup for marketing platform"""
    
    # 1. Set up main logger with rotation
    logger = logging.getLogger('marketing_platform')
    logger.setLevel(logging.DEBUG)
    
    # 2. Console handler for INFO+
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(levelname)-8s: %(message)s'
    ))
    
    # 3. File handler with rotation for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        'marketing_platform.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    ))
    
    # 4. Error file for ERROR+ only
    error_handler = logging.handlers.RotatingFileHandler(
        'marketing_errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d\n'
        '%(message)s\n'
    ))
    
    # 5. Add handlers
    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # 6. Capture warnings
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger('py.warnings')
    warnings_logger.addHandler(file_handler)
    
    # 7. Set up filters for production
    warnings.filterwarnings('always', category=DeprecationWarning)
    warnings.filterwarnings('always', category=ResourceWarning)
    warnings.filterwarnings('once', category=PerformanceWarning)
    
    return logger

if __name__ == "__main__":
    demo_warnings_and_logging()
    print("\n" + "="*50)
    print("Production setup example:")
    prod_logger = marketing_platform_logger_setup()
    prod_logger.info("Marketing platform logger configured")
    warnings.warn("Example warning in production setup", UserWarning)