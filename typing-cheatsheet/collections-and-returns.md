# Python Typing: Collections & Multiple Return Values

## List Types & Operations

### Basic List Typing
```python
from typing import List, MutableSequence, Sequence

# Concrete type
numbers: List[int] = [1, 2, 3]
mixed: List[int | str] = [1, "two", 3]

# Abstract types (more flexible)
read_only: Sequence[int] = [1, 2, 3]  # Can't modify
mutable: MutableSequence[int] = [1, 2, 3]  # Can modify

# Nested lists
matrix: List[List[float]] = [[1.0, 2.0], [3.0, 4.0]]
jagged: List[List[int]] = [[1], [2, 3], [4, 5, 6]]
```

### List Comprehension Typing
```python
from typing import List, Iterable

def process_items(items: Iterable[str]) -> List[int]:
    return [len(item) for item in items]

# Type inference in comprehensions
data: List[str] = ["a", "bb", "ccc"]
lengths: List[int] = [len(x) for x in data]
filtered: List[str] = [x for x in data if len(x) > 1]
```

### Advanced List Patterns
```python
from typing import List, TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Bounded lists
from typing import Literal

SmallList = List[int]  # Can have any length
FixedList = tuple[int, int, int]  # Exactly 3 elements
```

## Dictionary Types

### Basic Dictionary Typing
```python
from typing import Dict, Mapping, MutableMapping

# Simple dictionary
scores: Dict[str, int] = {"alice": 95, "bob": 87}

# Read-only vs mutable
read_only: Mapping[str, int] = {"x": 1}  # Can't modify
mutable: MutableMapping[str, int] = {"x": 1}  # Can modify

# Nested dictionaries
user_data: Dict[str, Dict[str, Any]] = {
    "user1": {"name": "Alice", "age": 30},
    "user2": {"name": "Bob", "age": 25}
}
```

### TypedDict for Structured Data
```python
from typing import TypedDict, Required, NotRequired

class UserProfile(TypedDict):
    id: int
    username: str
    email: str
    age: NotRequired[int]  # Optional field

class StrictConfig(TypedDict, total=True):  # All fields required
    host: str
    port: int
    debug: bool

# Usage
user: UserProfile = {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
}

# Nested TypedDict
class Address(TypedDict):
    street: str
    city: str
    zip: str

class Person(TypedDict):
    name: str
    address: Address

person: Person = {
    "name": "Alice",
    "address": {"street": "123 Main", "city": "NYC", "zip": "10001"}
}
```

### Dictionary Comprehension Typing
```python
from typing import Dict, List

names: List[str] = ["alice", "bob", "charlie"]
# Type is inferred as Dict[str, int]
name_lengths = {name: len(name) for name in names}

# Explicit typing
squares: Dict[int, int] = {x: x**2 for x in range(10)}
```

## Multiple Return Values

### Tuple Returns
```python
from typing import Tuple

def get_dimensions() -> Tuple[int, int]:
    return (1920, 1080)

def parse_data(text: str) -> Tuple[bool, str, int]:
    # Returns (success, message, code)
    return (True, "Parsed successfully", 200)

# Variable length tuples
def get_values() -> Tuple[int, ...]:
    return (1, 2, 3, 4, 5)

# Unpacking with types
width: int
height: int
width, height = get_dimensions()
```

### NamedTuple for Clarity
```python
from typing import NamedTuple

class Result(NamedTuple):
    success: bool
    message: str
    data: List[int]

def process() -> Result:
    return Result(True, "Done", [1, 2, 3])

# Usage
result = process()
if result.success:
    print(result.message)
    print(result.data)

# Alternative definition
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
def get_point() -> Point:
    return Point(10, 20)
```

### Union Returns for Error Handling
```python
from typing import Union, Optional

def divide(a: float, b: float) -> Union[float, str]:
    if b == 0:
        return "Cannot divide by zero"
    return a / b

def find_user(id: int) -> Optional[Dict[str, Any]]:
    # Returns None if not found
    if id == 1:
        return {"name": "Alice", "age": 30}
    return None

# Better pattern with explicit types
from typing import Literal

class Success:
    status: Literal["ok"] = "ok"
    value: float

class Error:
    status: Literal["error"] = "error"
    message: str

def safe_divide(a: float, b: float) -> Success | Error:
    if b == 0:
        err = Error()
        err.message = "Division by zero"
        return err
    result = Success()
    result.value = a / b
    return result
```

### Dataclass Returns
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResult:
    items: List[str]
    total_count: int
    page: int
    has_more: bool

def search(query: str, page: int = 1) -> SearchResult:
    # Simulated search
    return SearchResult(
        items=["result1", "result2"],
        total_count=100,
        page=page,
        has_more=True
    )

# Using the result
result = search("python")
for item in result.items:
    print(item)
if result.has_more:
    next_page = search("python", result.page + 1)
```

## Complex Collection Patterns

### Nested Collections
```python
from typing import Dict, List, Set, Tuple

# Graph adjacency list
Graph = Dict[str, List[str]]
graph: Graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"]
}

# Inverted index
Index = Dict[str, Set[int]]
word_index: Index = {
    "python": {1, 5, 10},
    "typing": {2, 5, 8},
}

# Coordinate mapping
CoordMap = Dict[Tuple[int, int], str]
grid: CoordMap = {
    (0, 0): "start",
    (1, 0): "path",
    (1, 1): "end"
}
```

### ChainMap & Counter Types
```python
from collections import ChainMap, Counter
from typing import Dict, Mapping

# ChainMap for layered configs
defaults: Dict[str, Any] = {"debug": False, "port": 8080}
user_config: Dict[str, Any] = {"port": 3000}
config: Mapping[str, Any] = ChainMap(user_config, defaults)

# Counter for frequency analysis
from typing import Counter as CounterType
word_counts: CounterType[str] = Counter(["apple", "banana", "apple"])
```

### DefaultDict Typing
```python
from collections import defaultdict
from typing import DefaultDict, List, Set

# List as default
groups: DefaultDict[str, List[int]] = defaultdict(list)
groups["even"].append(2)
groups["odd"].append(1)

# Set as default
tags: DefaultDict[str, Set[str]] = defaultdict(set)
tags["python"].add("language")
tags["python"].add("scripting")

# Custom default factory
def default_user() -> Dict[str, Any]:
    return {"name": "Unknown", "age": 0}

users: DefaultDict[int, Dict[str, Any]] = defaultdict(default_user)
```

## Performance Considerations

### Memory-Efficient Types
```python
from typing import Iterator, Generator, Iterable

# Iterator (lazy evaluation)
def large_range() -> Iterator[int]:
    return iter(range(1_000_000))

# Generator (memory efficient)
def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Iterable (most generic)
def process(items: Iterable[int]) -> List[int]:
    return [x * 2 for x in items]
```

### Immutable Collections
```python
from typing import FrozenSet, Tuple
from types import MappingProxyType

# Immutable set
constants: FrozenSet[str] = frozenset(["PI", "E", "PHI"])

# Immutable sequence
coords: Tuple[float, float] = (10.5, 20.3)

# Read-only dict view
original: Dict[str, int] = {"a": 1, "b": 2}
readonly: Mapping[str, int] = MappingProxyType(original)
```

## Common Patterns

### Pipeline Pattern
```python
from typing import List, Callable, TypeVar

T = TypeVar('T')
def pipeline(data: T, *funcs: Callable[[T], T]) -> T:
    for func in funcs:
        data = func(data)
    return data

# Usage
def double(x: List[int]) -> List[int]:
    return [i * 2 for i in x]

def add_one(x: List[int]) -> List[int]:
    return [i + 1 for i in x]

result = pipeline([1, 2, 3], double, add_one)  # [3, 5, 7]
```

### Accumulator Pattern
```python
from typing import List, Tuple, Any
from functools import reduce

def accumulate_stats(numbers: List[float]) -> Tuple[float, float, float]:
    """Returns (sum, mean, max)"""
    total = sum(numbers)
    mean = total / len(numbers)
    maximum = max(numbers)
    return total, mean, maximum

# With reduce
def process_items(items: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    def accumulator(acc: Dict[str, List[Any]], item: Dict[str, Any]) -> Dict[str, List[Any]]:
        for key, value in item.items():
            acc.setdefault(key, []).append(value)
        return acc

    return reduce(accumulator, items, {})
```