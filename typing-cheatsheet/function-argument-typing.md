# Python Typing: Function Arguments & Schemas

## Basic Function Arguments

### Simple Arguments
```python
from typing import Optional, Union

def greet(name: str, age: int, active: bool = True) -> str:
    return f"{name} is {age} years old"

def calculate(x: float, y: float, operation: str = "add") -> float:
    if operation == "add":
        return x + y
    return x - y

# Optional parameters
def connect(host: str, port: int, timeout: Optional[float] = None) -> bool:
    if timeout is None:
        timeout = 30.0
    return True

# Union types
def process_id(id_value: Union[int, str]) -> str:
    if isinstance(id_value, int):
        return f"ID-{id_value:04d}"
    return id_value
```

### Default Arguments with Mutable Types
```python
from typing import List, Dict, Optional

# Wrong way - mutable default
def bad_append(item: str, items: List[str] = []) -> List[str]:  # Don't do this!
    items.append(item)
    return items

# Correct way - use None
def good_append(item: str, items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# With dict
def process_config(
    name: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if config is None:
        config = {}
    config["name"] = name
    return config
```

## Dictionary Arguments with Schemas

### TypedDict for Structured Dicts
```python
from typing import TypedDict, NotRequired, Required

class UserData(TypedDict):
    id: int
    username: str
    email: str
    age: NotRequired[int]  # Optional field
    verified: NotRequired[bool]

def create_user(data: UserData) -> str:
    user_id = data["id"]
    username = data["username"]
    email = data["email"]
    age = data.get("age", 0)  # Safe access for optional
    return f"User {username} created with ID {user_id}"

# Usage
user_info: UserData = {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
}
result = create_user(user_info)
```

### Nested TypedDict Schemas
```python
from typing import TypedDict, List

class Address(TypedDict):
    street: str
    city: str
    country: str
    zip_code: str

class ContactInfo(TypedDict):
    phone: str
    email: str
    address: Address

class Employee(TypedDict):
    id: int
    name: str
    department: str
    contact: ContactInfo
    skills: List[str]

def process_employee(employee: Employee) -> str:
    return f"""
    Employee: {employee['name']}
    Department: {employee['department']}
    Location: {employee['contact']['address']['city']}
    Skills: {', '.join(employee['skills'])}
    """

# Usage
emp: Employee = {
    "id": 1,
    "name": "Bob",
    "department": "Engineering",
    "contact": {
        "phone": "555-0100",
        "email": "bob@company.com",
        "address": {
            "street": "123 Main St",
            "city": "NYC",
            "country": "USA",
            "zip_code": "10001"
        }
    },
    "skills": ["Python", "TypeScript", "Docker"]
}
```

### Dynamic Dict Keys with Specific Value Types
```python
from typing import Dict, Mapping, MutableMapping

# All keys are strings, all values are ints
def count_words(text: str) -> Dict[str, int]:
    words: Dict[str, int] = {}
    for word in text.split():
        words[word] = words.get(word, 0) + 1
    return words

# Mixed value types but known keys
ConfigValue = Union[str, int, bool, List[str]]
Config = Dict[str, ConfigValue]

def load_config(settings: Config) -> None:
    debug = settings.get("debug", False)
    port = settings.get("port", 8080)
    allowed_hosts = settings.get("allowed_hosts", [])

# Read-only dict parameter
def validate_settings(config: Mapping[str, Any]) -> bool:
    return "api_key" in config and "endpoint" in config

# Mutable dict parameter
def update_cache(cache: MutableMapping[str, str], key: str, value: str) -> None:
    cache[key] = value
```

## Variable Arguments (*args, **kwargs)

### Typed *args
```python
from typing import Tuple

def sum_all(*numbers: int) -> int:
    return sum(numbers)

def concatenate(*strings: str) -> str:
    return "".join(strings)

def process_mixed(*values: Union[int, str]) -> List[str]:
    return [str(v) for v in values]

# Homogeneous variable args
def average(*grades: float) -> float:
    return sum(grades) / len(grades) if grades else 0.0
```

### Typed **kwargs
```python
from typing import Any, Dict

def create_config(**options: str) -> Dict[str, str]:
    return options

def build_query(**params: Union[str, int]) -> str:
    parts = [f"{k}={v}" for k, v in params.items()]
    return "&".join(parts)

# With TypedDict and Unpack (Python 3.11+)
from typing import TypedDict, Unpack

class ServerOptions(TypedDict):
    host: str
    port: int
    debug: bool
    timeout: NotRequired[float]

def start_server(**options: Unpack[ServerOptions]) -> None:
    host = options["host"]
    port = options["port"]
    debug = options.get("debug", False)
    print(f"Starting server on {host}:{port}")

# Usage
start_server(host="localhost", port=8080, debug=True)
```

### Combining Regular, *args, and **kwargs
```python
from typing import Any, Dict

def flexible_function(
    required: str,
    optional: int = 0,
    *extra_args: str,
    **extra_kwargs: Any
) -> Dict[str, Any]:
    return {
        "required": required,
        "optional": optional,
        "args": extra_args,
        "kwargs": extra_kwargs
    }

# Advanced pattern
def api_call(
    endpoint: str,
    *path_params: Union[str, int],
    method: str = "GET",
    **query_params: str
) -> str:
    path = "/".join(str(p) for p in path_params)
    query = "&".join(f"{k}={v}" for k, v in query_params.items())
    return f"{method} {endpoint}/{path}?{query}"
```

## Callback Functions

### Basic Callbacks
```python
from typing import Callable, Optional

def process_data(
    data: List[int],
    callback: Callable[[int], int]
) -> List[int]:
    return [callback(x) for x in data]

def with_retry(
    func: Callable[[], str],
    on_error: Optional[Callable[[Exception], None]] = None,
    max_retries: int = 3
) -> Optional[str]:
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if on_error:
                on_error(e)
    return None

# Complex callback signatures
Handler = Callable[[str, int], bool]
Processor = Callable[[Dict[str, Any]], Optional[str]]

def register_handler(
    event: str,
    handler: Handler
) -> None:
    print(f"Registered {handler.__name__} for {event}")
```

### Callbacks with ParamSpec (3.10+)
```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec('P')
R = TypeVar('R')

def with_logging(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper

@with_logging
def add(x: int, y: int) -> int:
    return x + y

# Preserves original signature
result = add(5, 3)  # Type checker knows this returns int
```

## Advanced Argument Patterns

### Literal Types for Specific Values
```python
from typing import Literal, overload

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

def log(message: str, level: LogLevel = "INFO") -> None:
    print(f"[{level}] {message}")

# Overloaded based on literal
@overload
def fetch_data(format: Literal["json"]) -> Dict[str, Any]: ...

@overload
def fetch_data(format: Literal["csv"]) -> List[List[str]]: ...

@overload
def fetch_data(format: Literal["xml"]) -> str: ...

def fetch_data(format: str) -> Union[Dict[str, Any], List[List[str]], str]:
    if format == "json":
        return {"data": "value"}
    elif format == "csv":
        return [["col1", "col2"], ["val1", "val2"]]
    else:
        return "<xml>data</xml>"
```

### Protocol-Based Arguments
```python
from typing import Protocol

class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...

def find_min(items: List[Comparable]) -> Comparable:
    return min(items)

class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...

def save_objects(objects: List[Serializable], filename: str) -> None:
    import json
    data = [obj.to_dict() for obj in objects]
    with open(filename, 'w') as f:
        json.dump(data, f)
```

### Annotated for Validation
```python
from typing import Annotated

# Custom validators (for documentation/tooling)
PositiveInt = Annotated[int, "Must be positive"]
Email = Annotated[str, "Valid email format"]
Percentage = Annotated[float, "Value between 0 and 100"]

def create_account(
    username: Annotated[str, "3-20 characters"],
    age: PositiveInt,
    email: Email,
    discount: Percentage = 0.0
) -> bool:
    # Runtime validation would go here
    return True

# With multiple metadata
UserId = Annotated[int, "positive", "unique", "primary_key"]

def get_user(
    user_id: UserId,
    include_deleted: Annotated[bool, "Include soft-deleted records"] = False
) -> Optional[Dict[str, Any]]:
    return {"id": user_id, "name": "Alice"}
```

### Final Arguments
```python
from typing import Final

def process_with_constants(
    data: List[float],
    SCALE: Final[float] = 1.0,  # Indicates shouldn't be modified
    OFFSET: Final[float] = 0.0
) -> List[float]:
    # SCALE = 2.0  # Type checker warns against this
    return [x * SCALE + OFFSET for x in data]
```

## Complex Real-World Examples

### API Endpoint Handler
```python
from typing import TypedDict, Literal, Optional, Dict, Any

class RequestHeaders(TypedDict):
    content_type: str
    authorization: NotRequired[str]
    user_agent: NotRequired[str]

class RequestBody(TypedDict):
    action: Literal["create", "update", "delete"]
    resource: str
    data: Dict[str, Any]

class Response(TypedDict):
    status: int
    message: str
    data: Optional[Dict[str, Any]]

def handle_api_request(
    method: Literal["GET", "POST", "PUT", "DELETE"],
    path: str,
    headers: RequestHeaders,
    body: Optional[RequestBody] = None,
    query_params: Optional[Dict[str, str]] = None
) -> Response:
    # Process request
    if method == "POST" and body:
        action = body["action"]
        resource = body["resource"]
        return {
            "status": 201,
            "message": f"Created {resource}",
            "data": body["data"]
        }
    return {
        "status": 200,
        "message": "Success",
        "data": None
    }
```

### Database Query Builder
```python
from typing import TypedDict, List, Optional, Union, Literal

class WhereClause(TypedDict):
    column: str
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"]
    value: Union[str, int, float, List[Any]]

class JoinClause(TypedDict):
    table: str
    on: str
    type: Literal["INNER", "LEFT", "RIGHT", "FULL"]

def build_query(
    table: str,
    columns: List[str] = ["*"],
    where: Optional[List[WhereClause]] = None,
    joins: Optional[List[JoinClause]] = None,
    order_by: Optional[Dict[str, Literal["ASC", "DESC"]]] = None,
    limit: Optional[int] = None
) -> str:
    query = f"SELECT {', '.join(columns)} FROM {table}"

    if joins:
        for join in joins:
            query += f" {join['type']} JOIN {join['table']} ON {join['on']}"

    if where:
        conditions = []
        for clause in where:
            conditions.append(f"{clause['column']} {clause['operator']} {clause['value']}")
        query += f" WHERE {' AND '.join(conditions)}"

    if order_by:
        orders = [f"{col} {dir}" for col, dir in order_by.items()]
        query += f" ORDER BY {', '.join(orders)}"

    if limit:
        query += f" LIMIT {limit}"

    return query

# Usage
query = build_query(
    table="users",
    columns=["id", "name", "email"],
    where=[
        {"column": "age", "operator": ">", "value": 18},
        {"column": "status", "operator": "=", "value": "active"}
    ],
    order_by={"created_at": "DESC"},
    limit=10
)
```

### Configuration with Validation
```python
from typing import TypedDict, Literal, List, Union
from dataclasses import dataclass

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: NotRequired[int]
    timeout: NotRequired[float]

class CacheConfig(TypedDict):
    backend: Literal["redis", "memcached", "memory"]
    host: NotRequired[str]
    port: NotRequired[int]
    ttl: int

class LogConfig(TypedDict):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    format: str
    handlers: List[Literal["console", "file", "syslog"]]

class AppConfig(TypedDict):
    name: str
    version: str
    debug: bool
    database: DatabaseConfig
    cache: CacheConfig
    logging: LogConfig

def validate_and_init(config: AppConfig) -> bool:
    # Validate required fields exist
    if config["database"]["port"] < 1 or config["database"]["port"] > 65535:
        raise ValueError("Invalid port number")

    # Set defaults for optional fields
    if "pool_size" not in config["database"]:
        config["database"]["pool_size"] = 10

    if config["cache"]["backend"] in ["redis", "memcached"]:
        if "host" not in config["cache"]:
            raise ValueError(f"{config['cache']['backend']} requires host")

    return True

# Usage
app_config: AppConfig = {
    "name": "MyApp",
    "version": "1.0.0",
    "debug": True,
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "user": "admin",
        "password": "secret"
    },
    "cache": {
        "backend": "redis",
        "host": "localhost",
        "port": 6379,
        "ttl": 3600
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(message)s",
        "handlers": ["console", "file"]
    }
}
```