#!/usr/bin/env python3
"""
Defensive Programming: Input Validation and Type Checking
"""

from typing import Union, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

# PRINCIPLE 1: Fail Fast, Fail Clearly
# Bad: Let errors propagate mysteriously
def calculate_percentage_bad(value, total):
    return (value / total) * 100  # Will crash with cryptic error if total=0

# Good: Validate inputs immediately
def calculate_percentage_good(value: float, total: float) -> float:
    """Calculate percentage with validation"""
    if not isinstance(value, (int, float)):
        raise TypeError(f"'value' must be numeric, got {type(value).__name__}")
    if not isinstance(total, (int, float)):
        raise TypeError(f"'total' must be numeric, got {type(total).__name__}")
    if total == 0:
        raise ValueError("Cannot calculate percentage with total=0")
    if value < 0 or total < 0:
        raise ValueError("Values must be non-negative")
    if value > total:
        raise ValueError(f"Value ({value}) cannot exceed total ({total})")
    
    return (value / total) * 100

# PRINCIPLE 2: Use Type Hints and Runtime Validation
from typing import TypeVar, Type

T = TypeVar('T')

def validate_type(value: Any, expected_type: Type[T], param_name: str) -> T:
    """Generic type validator"""
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Parameter '{param_name}' must be {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
    return value

# PRINCIPLE 3: Validate Value Ranges
class RangeValidator:
    """Validates numeric values are within acceptable ranges"""
    
    @staticmethod
    def validate_percentage(value: float, param_name: str = "value") -> float:
        """Ensure value is between 0 and 100"""
        if not 0 <= value <= 100:
            raise ValueError(f"{param_name} must be between 0 and 100, got {value}")
        return value
    
    @staticmethod
    def validate_positive(value: float, param_name: str = "value") -> float:
        """Ensure value is positive"""
        if value <= 0:
            raise ValueError(f"{param_name} must be positive, got {value}")
        return value
    
    @staticmethod
    def validate_port(port: int) -> int:
        """Validate network port number"""
        if not isinstance(port, int):
            raise TypeError(f"Port must be integer, got {type(port).__name__}")
        if not 1 <= port <= 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {port}")
        return port

# PRINCIPLE 4: Validate Complex Data Structures
class DataValidator:
    """Validates complex data structures"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email format: {email}")
        
        return email
    
    @staticmethod
    def validate_dict_schema(data: dict, schema: dict) -> dict:
        """Validate dictionary against a schema"""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")
        
        # Check required fields
        for field, field_type in schema.items():
            if field not in data:
                raise KeyError(f"Missing required field: {field}")
            
            if not isinstance(data[field], field_type):
                raise TypeError(
                    f"Field '{field}' must be {field_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )
        
        return data
    
    @staticmethod
    def validate_list_items(items: list, item_type: type, min_length: int = 0) -> list:
        """Validate all items in a list are of the same type"""
        if not isinstance(items, list):
            raise TypeError(f"Expected list, got {type(items).__name__}")
        
        if len(items) < min_length:
            raise ValueError(f"List must have at least {min_length} items, got {len(items)}")
        
        for i, item in enumerate(items):
            if not isinstance(item, item_type):
                raise TypeError(
                    f"Item at index {i} must be {item_type.__name__}, "
                    f"got {type(item).__name__}"
                )
        
        return items

# PRINCIPLE 5: Use Enums for Fixed Sets of Values
class Status(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

def process_task(task_id: int, status: Status):
    """Process task with enum validation"""
    # No need to validate status - enum ensures it's valid
    print(f"Processing task {task_id} with status {status.value}")

# PRINCIPLE 6: Builder Pattern with Validation
@dataclass
class DatabaseConfig:
    """Database configuration with validation"""
    host: str
    port: int
    database: str
    username: str
    password: str
    
    def __post_init__(self):
        """Validate after initialization"""
        if not self.host:
            raise ValueError("Host cannot be empty")
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid port: {self.port}")
        if not self.database:
            raise ValueError("Database name cannot be empty")
        if not self.username:
            raise ValueError("Username cannot be empty")
        # Note: In production, never log passwords!
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")

# PRINCIPLE 7: Defensive Copying
class SafeDataProcessor:
    """Demonstrates defensive copying to prevent external modification"""
    
    def __init__(self, data: List[dict]):
        # Defensive copy - prevents external modification
        self._data = [item.copy() for item in data]
    
    def process(self, filters: dict) -> List[dict]:
        """Process data without modifying internal state"""
        # Work on a copy, not the original
        result = [item.copy() for item in self._data]
        
        # Apply filters (simplified example)
        if 'min_value' in filters:
            min_val = filters['min_value']
            result = [item for item in result if item.get('value', 0) >= min_val]
        
        return result
    
    @property
    def data(self) -> List[dict]:
        """Return a copy to prevent external modification"""
        return [item.copy() for item in self._data]

# PRINCIPLE 8: Context Managers for Resource Safety
class SafeFileProcessor:
    """Safely process files with automatic cleanup"""
    
    def __init__(self, filepath: str, mode: str = 'r'):
        self.filepath = filepath
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        # Validate before opening
        if self.mode not in ['r', 'w', 'a', 'rb', 'wb']:
            raise ValueError(f"Invalid file mode: {self.mode}")
        
        try:
            self.file = open(self.filepath, self.mode)
            return self
        except IOError as e:
            raise IOError(f"Cannot open file {self.filepath}: {e}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Return False to propagate any exception

# PRINCIPLE 9: Validation Decorators
def validate_arguments(**validations):
    """Decorator for automatic argument validation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Apply validations
            for param_name, validator in validations.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    try:
                        bound.arguments[param_name] = validator(value)
                    except Exception as e:
                        raise ValueError(f"Validation failed for '{param_name}': {e}")
            
            return func(**bound.arguments)
        return wrapper
    return decorator

# Example usage of validation decorator
@validate_arguments(
    age=lambda x: RangeValidator.validate_positive(x, "age"),
    email=DataValidator.validate_email
)
def create_user(name: str, age: int, email: str):
    """Create user with automatic validation"""
    return {
        'name': name,
        'age': age,
        'email': email
    }

# PRINCIPLE 10: Sanitization for Security
class InputSanitizer:
    """Sanitize inputs to prevent injection attacks"""
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """Sanitize SQL identifiers (table/column names)"""
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier}")
        
        # Check against SQL keywords (simplified list)
        sql_keywords = ['SELECT', 'DROP', 'INSERT', 'UPDATE', 'DELETE']
        if identifier.upper() in sql_keywords:
            raise ValueError(f"Identifier cannot be SQL keyword: {identifier}")
        
        return identifier
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        # Remove path separators and null bytes
        filename = filename.replace('/', '').replace('\\', '').replace('\0', '')
        
        # Remove leading dots (hidden files)
        filename = filename.lstrip('.')
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        # Ensure it's not empty
        if not filename:
            raise ValueError("Filename cannot be empty after sanitization")
        
        return filename

# Demo function showing all principles
def demo_defensive_programming():
    """Demonstrate defensive programming principles"""
    
    print("1. Type validation:")
    try:
        calculate_percentage_good("50", 100)  # Will fail - wrong type
    except TypeError as e:
        print(f"  Caught: {e}")
    
    print("\n2. Range validation:")
    try:
        RangeValidator.validate_percentage(150, "discount")
    except ValueError as e:
        print(f"  Caught: {e}")
    
    print("\n3. Complex data validation:")
    schema = {'id': int, 'name': str, 'active': bool}
    try:
        DataValidator.validate_dict_schema(
            {'id': 1, 'name': 'Test'},  # Missing 'active'
            schema
        )
    except KeyError as e:
        print(f"  Caught: {e}")
    
    print("\n4. Email validation:")
    try:
        email = DataValidator.validate_email("user@example.com")
        print(f"  Valid email: {email}")
        DataValidator.validate_email("invalid-email")
    except ValueError as e:
        print(f"  Caught: {e}")
    
    print("\n5. Decorator validation:")
    try:
        user = create_user("John", 25, "john@example.com")
        print(f"  Created user: {user}")
        create_user("Jane", -5, "jane@example.com")  # Invalid age
    except ValueError as e:
        print(f"  Caught: {e}")
    
    print("\n6. Defensive copying:")
    original_data = [{'value': 10}, {'value': 20}]
    processor = SafeDataProcessor(original_data)
    
    # Modify original - won't affect processor
    original_data[0]['value'] = 999
    
    result = processor.process({'min_value': 15})
    print(f"  Processor data unchanged: {processor.data}")
    print(f"  Filtered result: {result}")

if __name__ == "__main__":
    demo_defensive_programming()