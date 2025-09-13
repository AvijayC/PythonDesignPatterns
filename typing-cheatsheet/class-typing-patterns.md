# Python Typing: Class Patterns & User-Defined Types

## Basic Class Typing

### Constructor & Instance Variables
```python
from typing import Optional, List, Dict

class User:
    def __init__(self, name: str, age: int, email: Optional[str] = None) -> None:
        self.name: str = name
        self.age: int = age
        self.email: Optional[str] = email
        self._created_at: float = time.time()  # Private attribute
        self.tags: List[str] = []  # Mutable default

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

    def get_info(self) -> Dict[str, Any]:
        return {"name": self.name, "age": self.age}
```

### Class Variables & Instance Variables
```python
from typing import ClassVar, List

class Counter:
    # Class variable (shared by all instances)
    instance_count: ClassVar[int] = 0
    registry: ClassVar[List['Counter']] = []

    def __init__(self, initial: int = 0) -> None:
        # Instance variable
        self.value: int = initial
        Counter.instance_count += 1
        Counter.registry.append(self)

    @classmethod
    def get_total_instances(cls) -> int:
        return cls.instance_count
```

## Properties & Descriptors

### Property Typing
```python
from typing import Optional

class Temperature:
    def __init__(self, celsius: float = 0.0) -> None:
        self._celsius: float = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5/9
```

### Descriptor Protocol
```python
from typing import Any, Optional, Type

class ValidatedAttribute:
    def __init__(self, min_value: int = 0) -> None:
        self.min_value = min_value
        self.data: Dict[int, int] = {}

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> int:
        if obj is None:
            return self
        return self.data.get(id(obj), 0)

    def __set__(self, obj: Any, value: int) -> None:
        if value < self.min_value:
            raise ValueError(f"Value must be >= {self.min_value}")
        self.data[id(obj)] = value

class Product:
    price = ValidatedAttribute(min_value=0)
    quantity = ValidatedAttribute(min_value=0)

    def __init__(self, price: int, quantity: int) -> None:
        self.price = price
        self.quantity = quantity
```

## Method Overloading & Variations

### Method Overloading
```python
from typing import overload, Union, Literal

class Calculator:
    @overload
    def add(self, x: int, y: int) -> int: ...

    @overload
    def add(self, x: float, y: float) -> float: ...

    @overload
    def add(self, x: str, y: str) -> str: ...

    def add(self, x: Union[int, float, str], y: Union[int, float, str]) -> Union[int, float, str]:
        if isinstance(x, str) and isinstance(y, str):
            return x + y
        return x + y  # Works for numbers

    @overload
    def process(self, mode: Literal["fast"]) -> int: ...

    @overload
    def process(self, mode: Literal["accurate"]) -> float: ...

    def process(self, mode: str) -> Union[int, float]:
        if mode == "fast":
            return 42
        return 3.14159
```

### Static & Class Methods
```python
from typing import Type, TypeVar, List

T = TypeVar('T', bound='Model')

class Model:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        import json
        return cls(json.loads(json_str))

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        return "id" in data and "name" in data

    @classmethod
    def create_batch(cls: Type[T], items: List[Dict[str, Any]]) -> List[T]:
        return [cls(item) for item in items]
```

## Inheritance & Protocols

### Basic Inheritance
```python
from typing import Optional, List

class Animal:
    def __init__(self, name: str, species: str) -> None:
        self.name: str = name
        self.species: str = species

    def make_sound(self) -> str:
        return "Some sound"

class Dog(Animal):
    def __init__(self, name: str, breed: Optional[str] = None) -> None:
        super().__init__(name, "Canis familiaris")
        self.breed: Optional[str] = breed

    def make_sound(self) -> str:  # Override
        return "Woof!"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetched {item}"
```

### Abstract Base Classes
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class DataProcessor(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.processed_count: int = 0

    @abstractmethod
    def process(self, data: List[float]) -> float:
        """Must be implemented by subclasses"""
        pass

    @abstractmethod
    def validate(self, data: List[float]) -> bool:
        pass

    def run(self, data: List[float]) -> Optional[float]:
        if self.validate(data):
            result = self.process(data)
            self.processed_count += 1
            return result
        return None

class AverageProcessor(DataProcessor):
    def process(self, data: List[float]) -> float:
        return sum(data) / len(data)

    def validate(self, data: List[float]) -> bool:
        return len(data) > 0
```

### Protocol Classes (Structural Subtyping)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...

@runtime_checkable
class Resizable(Protocol):
    width: int
    height: int

    def resize(self, factor: float) -> None: ...

# No explicit inheritance needed
class Circle:
    def draw(self) -> str:
        return "Drawing circle"

class Rectangle:
    def __init__(self) -> None:
        self.width: int = 100
        self.height: int = 50

    def draw(self) -> str:
        return "Drawing rectangle"

    def resize(self, factor: float) -> None:
        self.width = int(self.width * factor)
        self.height = int(self.height * factor)

def render(obj: Drawable) -> None:
    print(obj.draw())

# Both work without inheritance
render(Circle())
render(Rectangle())
```

## Generic Classes

### Basic Generic Class
```python
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Box(Generic[T]):
    def __init__(self, content: T) -> None:
        self._content: T = content

    def get(self) -> T:
        return self._content

    def set(self, content: T) -> None:
        self._content = content

# Usage
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")

class Pair(Generic[T]):
    def __init__(self, first: T, second: T) -> None:
        self.first: T = first
        self.second: T = second

    def swap(self) -> None:
        self.first, self.second = self.second, self.first
```

### Multiple Type Parameters
```python
from typing import TypeVar, Generic, Dict

K = TypeVar('K')
V = TypeVar('V')

class Cache(Generic[K, V]):
    def __init__(self) -> None:
        self._cache: Dict[K, V] = {}

    def get(self, key: K) -> Optional[V]:
        return self._cache.get(key)

    def set(self, key: K, value: V) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

# Usage
user_cache: Cache[int, str] = Cache()
user_cache.set(1, "Alice")
```

### Bounded Type Parameters
```python
from typing import TypeVar, Protocol

class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...
    def __le__(self, other: 'Comparable') -> bool: ...

T = TypeVar('T', bound=Comparable)

class SortedList(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []

    def add(self, item: T) -> None:
        import bisect
        bisect.insort(self._items, item)

    def get_min(self) -> Optional[T]:
        return self._items[0] if self._items else None
```

## Advanced Patterns

### Self Type (Python 3.11+)
```python
from typing import Self

class Shape:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y

    def move(self, dx: float, dy: float) -> Self:
        self.x += dx
        self.y += dy
        return self

    def clone(self) -> Self:
        return self.__class__(self.x, self.y)

class Circle(Shape):
    def __init__(self, x: float = 0, y: float = 0, radius: float = 1) -> None:
        super().__init__(x, y)
        self.radius = radius

    def scale(self, factor: float) -> Self:
        self.radius *= factor
        return self
```

### Mixins with Typing
```python
from typing import Any, Dict

class JsonMixin:
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str) -> 'JsonMixin':
        import json
        obj = cls.__new__(cls)
        obj.__dict__ = json.loads(json_str)
        return obj

class TimestampMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        import time
        self.created_at: float = time.time()
        self.updated_at: float = time.time()

    def touch(self) -> None:
        import time
        self.updated_at = time.time()

class User(JsonMixin, TimestampMixin):
    def __init__(self, name: str, email: str) -> None:
        super().__init__()
        self.name = name
        self.email = email
```

### Dataclasses with Typing
```python
from dataclasses import dataclass, field
from typing import List, Optional, ClassVar

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    tags: List[str] = field(default_factory=list)
    _id: Optional[int] = field(default=None, init=False)

    # Class variable
    tax_rate: ClassVar[float] = 0.08

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("Price cannot be negative")

    @property
    def total_value(self) -> float:
        return self.price * self.quantity

    def apply_discount(self, percent: float) -> None:
        self.price *= (1 - percent / 100)

@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
```

### Context Managers
```python
from typing import Optional, Any
from types import TracebackType

class DatabaseConnection:
    def __init__(self, host: str, port: int = 5432) -> None:
        self.host = host
        self.port = port
        self.connection: Optional[Any] = None

    def __enter__(self) -> 'DatabaseConnection':
        print(f"Connecting to {self.host}:{self.port}")
        self.connection = f"Connection to {self.host}"
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> bool:
        print("Closing connection")
        self.connection = None
        return False  # Don't suppress exceptions

    def query(self, sql: str) -> List[Dict[str, Any]]:
        if not self.connection:
            raise RuntimeError("Not connected")
        return [{"result": "data"}]
```

### Callable Classes
```python
from typing import Callable, List

class Multiplier:
    def __init__(self, factor: int) -> None:
        self.factor = factor

    def __call__(self, value: int) -> int:
        return value * self.factor

class Pipeline:
    def __init__(self) -> None:
        self.steps: List[Callable[[Any], Any]] = []

    def add_step(self, func: Callable[[Any], Any]) -> 'Pipeline':
        self.steps.append(func)
        return self

    def __call__(self, data: Any) -> Any:
        for step in self.steps:
            data = step(data)
        return data

# Usage
double = Multiplier(2)
result = double(5)  # Returns 10

pipeline = Pipeline()
pipeline.add_step(lambda x: x * 2).add_step(lambda x: x + 1)
result = pipeline(5)  # Returns 11
```

## Metaclasses & Type Creation

### Basic Metaclass
```python
from typing import Any, Dict, Tuple

class SingletonMeta(type):
    _instances: Dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, name: str) -> None:
        self.name = name

# Always returns same instance
db1 = Database("main")
db2 = Database("other")
assert db1 is db2
```

### Type Annotations at Runtime
```python
from typing import get_type_hints, get_args, get_origin

class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    tags: List[str] = []

    @classmethod
    def get_field_types(cls) -> Dict[str, type]:
        return get_type_hints(cls)

    @classmethod
    def validate_type(cls, field: str, value: Any) -> bool:
        hints = get_type_hints(cls)
        if field in hints:
            expected_type = hints[field]
            origin = get_origin(expected_type)
            if origin is list:
                args = get_args(expected_type)
                return isinstance(value, list) and all(isinstance(item, args[0]) for item in value)
            return isinstance(value, expected_type)
        return False

# Usage
print(Config.get_field_types())  # {'host': str, 'port': int, ...}
print(Config.validate_type('port', 8080))  # True
print(Config.validate_type('port', "8080"))  # False
```