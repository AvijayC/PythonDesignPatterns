# Pydantic BaseModels: Complete Guide

## What are Pydantic BaseModels?

Pydantic BaseModels are Python classes that provide automatic data validation, serialization, and type hints. They're like dataclasses on steroids - they validate your data at runtime and provide clear error messages when data doesn't match expected types.

## Basic Definition and Usage

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

# Basic model with simple types
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 18  # Default value
    is_active: bool = True  # Another default

# Instantiation
user = User(id=1, name="Alice", email="alice@example.com")
# age defaults to 18, is_active defaults to True
```

## Fields with Default Values and Factories

```python
from typing import List
from datetime import datetime
from uuid import uuid4

class Product(BaseModel):
    # Required field (no default)
    name: str

    # Simple default value
    price: float = 0.0

    # Default factory (function that generates default)
    id: str = Field(default_factory=lambda: str(uuid4()))

    # Default factory for mutable types (NEVER use mutable defaults directly!)
    tags: List[str] = Field(default_factory=list)

    # Field with metadata and constraints
    quantity: int = Field(default=1, gt=0, le=1000, description="Stock quantity")

    # Optional field (can be None)
    description: Optional[str] = None

    # Timestamp with factory
    created_at: datetime = Field(default_factory=datetime.now)

# Instantiation examples
product1 = Product(name="Laptop")  # Uses all defaults
product2 = Product(
    name="Phone",
    price=999.99,
    tags=["electronics", "mobile"],
    quantity=50
)
```

## Custom Types and Nested Models

```python
from enum import Enum
from typing import List, Optional

# Custom Enum type
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

# Custom model as a field type
class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str = ""

    class Config:
        # Allow field assignment after creation
        validate_assignment = True

# Another custom model
class Company(BaseModel):
    name: str
    industry: str = "Technology"
    employee_count: int = 1

# Main model using custom types
class Employee(BaseModel):
    # Basic fields
    id: int
    name: str

    # Enum field with default
    role: UserRole = UserRole.USER

    # Nested model (required)
    primary_address: Address

    # Optional nested model
    work_address: Optional[Address] = None

    # List of nested models with default factory
    previous_addresses: List[Address] = Field(default_factory=list)

    # Nested model with default instance
    company: Company = Field(default_factory=lambda: Company(name="Default Corp"))

    # Dictionary field
    metadata: Dict[str, str] = Field(default_factory=dict)

# Instantiation with nested models
address = Address(street="123 Main St", city="Boston", country="USA", zip_code="02101")

employee = Employee(
    id=1,
    name="Bob Smith",
    role=UserRole.MODERATOR,
    primary_address=address,
    company=Company(name="Tech Inc", employee_count=500)
)

# Alternative: pass nested data as dictionaries
employee2 = Employee(
    id=2,
    name="Jane Doe",
    primary_address={
        "street": "456 Oak Ave",
        "city": "Seattle",
        "country": "USA"
    },
    work_address={
        "street": "789 Pine St",
        "city": "Seattle",
        "country": "USA",
        "zip_code": "98101"
    }
)
```

## Validators and Computed Fields

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional

class BankAccount(BaseModel):
    account_number: str
    balance: float = 0.0
    currency: str = "USD"
    overdraft_limit: float = Field(default=0.0, ge=0)

    # Field-level validator
    @validator('account_number')
    def validate_account_number(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Account number must be 10 digits')
        return v

    # Validator that depends on other fields
    @validator('balance')
    def check_overdraft(cls, v, values):
        # 'values' contains previously validated fields
        limit = values.get('overdraft_limit', 0)
        if v < -limit:
            raise ValueError(f'Balance cannot be below -{limit}')
        return v

    # Root validator (validates entire model)
    @root_validator
    def check_currency_limits(cls, values):
        currency = values.get('currency')
        balance = values.get('balance', 0)
        if currency == 'JPY' and abs(balance) > 1000000:
            raise ValueError('JPY accounts limited to 1M')
        return values

    # Computed property
    @property
    def available_funds(self) -> float:
        return self.balance + self.overdraft_limit

# Usage
account = BankAccount(
    account_number="1234567890",
    balance=1000.50,
    overdraft_limit=500
)
print(account.available_funds)  # 1500.50
```

## Advanced Configuration

```python
from pydantic import BaseModel, Field
import json

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str = "myapp"
    pool_size: int = Field(default=10, ge=1, le=100)

    class Config:
        # Control behavior
        validate_assignment = True  # Validate on attribute assignment
        use_enum_values = True  # Use enum values instead of enum instances

        # JSON serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

        # Field naming
        allow_population_by_field_name = True
        fields = {
            'password': {'exclude': True}  # Exclude from dict/json
        }

        # Example data for documentation
        schema_extra = {
            "example": {
                "host": "db.example.com",
                "port": 5432,
                "username": "admin",
                "password": "secret123",
                "database": "production"
            }
        }

# Loading from different sources
config_dict = {
    "host": "prod-db.com",
    "username": "dbadmin",
    "password": "secure_pass",
    "pool_size": 20
}

# From dictionary
config1 = DatabaseConfig(**config_dict)

# From JSON string
json_str = '{"host": "dev-db.com", "username": "dev", "password": "devpass"}'
config2 = DatabaseConfig.parse_raw(json_str)

# From file
config3 = DatabaseConfig.parse_file('config.json')

# Export to different formats
print(config1.dict(exclude={'password'}))  # Dictionary without password
print(config1.json(indent=2))  # JSON string
```

## Complex Real-World Example

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime, date
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class Attachment(BaseModel):
    filename: str
    size_bytes: int
    mime_type: str = "application/octet-stream"
    uploaded_at: datetime = Field(default_factory=datetime.now)

class Comment(BaseModel):
    author: str
    text: str
    created_at: datetime = Field(default_factory=datetime.now)
    edited: bool = False

class Task(BaseModel):
    # Core fields
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # Status and priority with defaults
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM

    # Dates
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None

    # Relations
    assignee: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Nested models
    attachments: List[Attachment] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)

    # Flexible metadata
    custom_fields: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)

    @validator('due_date')
    def due_date_not_in_past(cls, v):
        if v and v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v

    @validator('completed_at', always=True)
    def set_completed_at(cls, v, values):
        if values.get('status') == TaskStatus.DONE and not v:
            return datetime.now()
        return v

    def add_comment(self, author: str, text: str) -> None:
        """Helper method to add comments"""
        comment = Comment(author=author, text=text)
        self.comments.append(comment)

    def add_attachment(self, filename: str, size: int) -> None:
        """Helper method to add attachments"""
        attachment = Attachment(filename=filename, size_bytes=size)
        self.attachments.append(attachment)

# Creating a complex task
task = Task(
    title="Implement user authentication",
    description="Add OAuth2 authentication to the API",
    priority=Priority.HIGH,
    assignee="john.doe",
    tags=["backend", "security", "sprint-3"],
    due_date=date(2024, 12, 31),
    custom_fields={
        "estimated_hours": 16,
        "requires_review": True,
        "epic": "AUTH-001"
    }
)

# Adding nested data
task.add_comment("alice", "Should we use JWT or sessions?")
task.add_attachment("auth_design.pdf", 1024000)

# Update status (validates automatically if Config.validate_assignment = True)
task.status = TaskStatus.IN_PROGRESS

# Serialize for API response
api_response = task.dict(
    exclude={'custom_fields': {'epic'}},  # Exclude specific nested field
    exclude_none=True  # Don't include None values
)

# Serialize to JSON
json_data = task.json(indent=2)
```

## Key Takeaways

1. **Always use default_factory for mutable defaults** (lists, dicts, sets)
2. **Field() provides fine-grained control** over validation and metadata
3. **Nested models** work seamlessly - pass dicts or model instances
4. **Validators** can enforce complex business rules
5. **Config class** controls model behavior globally
6. **Type hints are enforced** - Pydantic validates at runtime
7. **Serialization is built-in** - easily convert to dict/JSON

## Common Patterns

```python
# Pattern 1: Optional with None default
optional_field: Optional[str] = None

# Pattern 2: List with empty default
items: List[str] = Field(default_factory=list)

# Pattern 3: Required field (no default)
required: str  # or use Field(...)

# Pattern 4: Constrained values
age: int = Field(ge=0, le=120)
email: str = Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Pattern 5: Computed default
timestamp: datetime = Field(default_factory=datetime.now)
uuid: str = Field(default_factory=lambda: str(uuid4()))
```

This covers the essential aspects of Pydantic BaseModels from basic usage to advanced patterns you'll encounter in production code.