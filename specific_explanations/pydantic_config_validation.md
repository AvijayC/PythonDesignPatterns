# Pydantic for Configuration Management & Auto-Validation

## What is Pydantic?

Pydantic is a Python library that uses type hints to validate data and manage settings. Think of it as a bouncer for your data - it checks that everything coming in matches what you expect, and converts it to the right type if possible.

## Why Pydantic Over Other Options?

- **Dataclasses**: Good for simple data storage, but no runtime validation
- **TypedDict**: Only for type checking, no runtime enforcement
- **Pydantic**: Runtime validation + type conversion + error messages + JSON support

Pydantic is perfect for configuration because it catches errors early and gives clear feedback about what's wrong.

## Basic Setup

```bash
pip install pydantic
```

## Core Concepts

### 1. Basic Model Definition

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Define an enum for controlled choices
class Environment(str, Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

# Your configuration class
class AppConfig(BaseModel):
    # Required fields (no default value)
    app_name: str
    version: str
    port: int

    # Optional fields (with defaults)
    debug: bool = False
    max_connections: int = 100

    # Field with validation constraints
    timeout: int = Field(default=30, ge=1, le=300)  # between 1-300 seconds

    # Enum field for controlled values
    environment: Environment = Environment.DEVELOPMENT

    # Complex types
    allowed_hosts: List[str] = []
    created_at: Optional[datetime] = None

    # Field with description
    api_key: str = Field(..., description="API key for external service")
```

### 2. Creating Config Objects (Fill Attributes One by One)

```python
# Method 1: All at once
config = AppConfig(
    app_name="MyAPI",
    version="1.0.0",
    port=8080,
    api_key="secret-key-123",
    debug=True,
    allowed_hosts=["localhost", "api.example.com"]
)

# Method 2: Using dict unpacking
config_data = {
    "app_name": "MyAPI",
    "version": "1.0.0",
    "port": 8080,
    "api_key": "secret-key-123"
}
config = AppConfig(**config_data)

# Method 3: From JSON file
import json

with open("config.json") as f:
    config_data = json.load(f)
    config = AppConfig(**config_data)
```

### 3. Automatic Validation Examples

```python
# This will work - automatic type conversion
config = AppConfig(
    app_name="MyApp",
    version="1.0.0",
    port="8080",  # String converted to int automatically
    api_key="key123"
)
print(config.port)  # Output: 8080 (as integer)

# This will fail - validation error
try:
    bad_config = AppConfig(
        app_name="MyApp",
        version="1.0.0",
        port="not_a_number",  # Can't convert to int
        api_key="key123"
    )
except ValueError as e:
    print(e)
    # Output: validation error for port
    #   value is not a valid integer

# This will fail - missing required field
try:
    incomplete_config = AppConfig(
        app_name="MyApp",
        version="1.0.0"
        # Missing port and api_key!
    )
except ValueError as e:
    print(e)
    # Output: 2 validation errors for AppConfig
    #   port: field required
    #   api_key: field required
```

### 4. Custom Validators

```python
from pydantic import BaseModel, validator, root_validator

class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database_name: str
    connection_pool_size: int = 10

    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

    @validator('connection_pool_size')
    def validate_pool_size(cls, v):
        if v < 1:
            raise ValueError('Pool size must be at least 1')
        if v > 100:
            raise ValueError('Pool size too large (max 100)')
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @root_validator
    def validate_connection(cls, values):
        # Check relationships between fields
        host = values.get('host')
        port = values.get('port')

        if host == 'localhost' and port == 5432:
            print("Warning: Using default PostgreSQL settings")

        return values
```

### 5. Nested Configurations

```python
class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None

class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str

class FullAppConfig(BaseModel):
    app_name: str
    version: str
    debug: bool = False

    # Nested configurations
    database: DatabaseConfig
    cache: RedisConfig

    # List of configs
    external_apis: List[dict] = []

# Usage
config = FullAppConfig(
    app_name="MyApp",
    version="2.0.0",
    database=DatabaseConfig(
        host="db.example.com",
        port=5432,
        name="myapp_db",
        user="dbuser",
        password="dbpass123"
    ),
    cache=RedisConfig(
        host="cache.example.com",
        password="redis123"
    )
)

# Access nested values
print(config.database.host)  # "db.example.com"
print(config.cache.port)     # 6379 (default value)
```

### 6. Loading from Environment Variables

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Will look for APP_NAME environment variable
    app_name: str

    # Will look for APP_PORT env var, default to 8000
    app_port: int = 8000

    # Will look for DEBUG env var
    debug: bool = False

    # Database URL from DATABASE_URL env var
    database_url: str

    # Custom env var name
    api_key: str = Field(..., env='SECRET_API_KEY')

    class Config:
        # Prefix for all env vars
        env_prefix = 'APP_'

        # Case sensitive env vars
        case_sensitive = False

        # Also load from .env file
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Usage
# Automatically loads from environment
settings = Settings()
```

### 7. Practical Example: Complete Configuration System

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum
import json
from pathlib import Path

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class ServiceConfig(BaseModel):
    """Configuration for a microservice"""

    # Basic settings
    service_name: str = Field(..., min_length=1, max_length=50)
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')  # Semantic versioning

    # Network settings
    host: str = "0.0.0.0"
    port: int = Field(8000, ge=1024, le=65535)

    # Performance settings
    workers: int = Field(4, ge=1, le=16)
    timeout: int = Field(30, ge=1, le=300)
    max_request_size: int = Field(1048576, ge=1024)  # 1MB default

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[Path] = None

    # Security
    api_keys: List[str] = []
    allowed_origins: List[str] = ["*"]
    rate_limit: int = Field(100, ge=1)  # requests per minute

    # Feature flags
    features: Dict[str, bool] = {}

    @validator('api_keys')
    def validate_api_keys(cls, v):
        if v:
            for key in v:
                if len(key) < 32:
                    raise ValueError(f'API keys must be at least 32 characters')
        return v

    @validator('log_file')
    def validate_log_file(cls, v):
        if v:
            # Ensure parent directory exists
            v = Path(v)
            if not v.parent.exists():
                v.parent.mkdir(parents=True, exist_ok=True)
        return v

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.dict(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, filepath: str):
        """Load configuration from JSON file"""
        with open(filepath) as f:
            data = json.load(f)
        return cls(**data)

    def display(self):
        """Pretty print configuration"""
        print("=" * 50)
        print(f"Service: {self.service_name} v{self.version}")
        print("=" * 50)
        for key, value in self.dict().items():
            if key == 'api_keys' and value:
                print(f"{key}: [REDACTED]")
            else:
                print(f"{key}: {value}")

# Usage example
if __name__ == "__main__":
    # Create configuration
    config = ServiceConfig(
        service_name="user-api",
        version="1.2.3",
        port=8080,
        workers=8,
        log_level=LogLevel.DEBUG,
        log_file="/var/log/user-api.log",
        api_keys=["a" * 32, "b" * 32],
        features={
            "new_auth": True,
            "beta_endpoints": False,
            "caching": True
        }
    )

    # Access values
    print(f"Running on {config.host}:{config.port}")
    print(f"Workers: {config.workers}")

    # Check feature flags
    if config.features.get("caching"):
        print("Caching is enabled")

    # Save and load
    config.save_to_file("service_config.json")
    loaded_config = ServiceConfig.load_from_file("service_config.json")
```

## Common Patterns & Best Practices

### 1. Immutable Configurations
```python
class ImmutableConfig(BaseModel):
    app_name: str
    port: int

    class Config:
        # Make it immutable after creation
        allow_mutation = False

config = ImmutableConfig(app_name="MyApp", port=8080)
# config.port = 9090  # This will raise an error!
```

### 2. Export Configurations
```python
config = AppConfig(...)

# To dictionary
config_dict = config.dict()

# To JSON string
config_json = config.json()

# To JSON with only changed fields
config_json = config.json(exclude_defaults=True)

# Exclude sensitive fields
safe_dict = config.dict(exclude={'password', 'api_key'})
```

### 3. Config Inheritance
```python
class BaseConfig(BaseModel):
    app_name: str
    version: str
    debug: bool = False

class DevConfig(BaseConfig):
    debug: bool = True
    hot_reload: bool = True

class ProdConfig(BaseConfig):
    debug: bool = False
    ssl_enabled: bool = True
    replicas: int = 3
```

## When to Use Pydantic Configs

✅ **Perfect for:**
- API settings
- Database configurations
- Service configurations
- Environment-specific settings
- Any structured data that needs validation

❌ **Not ideal for:**
- Simple scripts with 1-2 variables
- Frequently changing data (use regular classes)
- Performance-critical hot paths (validation has overhead)

## Common Gotchas & Solutions

1. **Field order matters for required fields** - Put required fields before optional ones
2. **Use `...` for required fields with no default** - `Field(...)` means required
3. **Validation happens on assignment** - Each time you create an object
4. **Type conversion is automatic** - "123" becomes 123 for int fields
5. **None vs missing** - Optional[str] = None is different from not providing the field

## Summary

Pydantic gives you:
- **Automatic validation** at object creation
- **Type conversion** (string "5" → int 5)
- **Clear error messages** when validation fails
- **JSON serialization** built-in
- **IDE autocomplete** for all fields
- **Runtime safety** for your configurations

This makes it perfect for configurations where you want to catch errors early rather than having your app crash later because of a typo in a config file.