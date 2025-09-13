# Python Typing Module Comprehensive Cheat Sheet

## Basic Types
```python
from typing import Any, None

x: int = 5
y: float = 3.14
name: str = "Alice"
flag: bool = True
data: bytes = b"raw"
nothing: None = None
anything: Any = "can be anything"
```

## Collections
```python
from typing import List, Dict, Set, Tuple, FrozenSet

numbers: List[int] = [1, 2, 3]
scores: Dict[str, float] = {"math": 95.5}
unique: Set[str] = {"a", "b", "c"}
coords: Tuple[int, int] = (10, 20)
fixed: Tuple[int, ...] = (1, 2, 3, 4)  # Variable length
frozen: FrozenSet[int] = frozenset([1, 2, 3])
```

## Optional & Union
```python
from typing import Optional, Union

maybe_int: Optional[int] = None  # Same as Union[int, None]
mixed: Union[str, int] = "text" or 42
multi: Union[str, int, float, None] = 3.14
```

## Type Aliases
```python
from typing import Dict, List, Tuple

UserId = int
UserData = Dict[str, Any]
Coordinate = Tuple[float, float]
Matrix = List[List[float]]

user_id: UserId = 12345
location: Coordinate = (37.7749, -122.4194)
```

## Callable Types
```python
from typing import Callable

Handler = Callable[[int, str], bool]
NoArgFunc = Callable[[], None]
AnyArgsFunc = Callable[..., int]

def process(func: Handler) -> None:
    result = func(42, "test")

callback: Callable[[str], None] = lambda x: print(x)
```

## Generics & TypeVar
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

def first(items: List[T]) -> T:
    return items[0]

class Box(Generic[T]):
    def __init__(self, content: T):
        self.content = content

    def get(self) -> T:
        return self.content

int_box: Box[int] = Box(42)
```

## Literal Types
```python
from typing import Literal

Mode = Literal["read", "write", "append"]
Status = Literal[200, 404, 500]

def open_file(mode: Mode) -> None:
    pass

status_code: Status = 200
```

## Protocol (Structural Subtyping)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(obj: Drawable) -> None:
    obj.draw()

render(Circle())  # Works without inheritance
```

## TypedDict
```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: NotRequired[str]  # Python 3.11+

class StrictUser(TypedDict, total=True):
    id: Required[int]
    name: Required[str]

user: UserDict = {"id": 1, "name": "Alice"}
```

## NewType
```python
from typing import NewType

UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

def get_user(user_id: UserId) -> str:
    return f"User {user_id}"

uid = UserId(42)
pid = ProductId(100)
# get_user(pid)  # Type error!
```

## Overload
```python
from typing import overload, Union

@overload
def process(x: int) -> str: ...

@overload
def process(x: str) -> int: ...

def process(x: Union[int, str]) -> Union[str, int]:
    if isinstance(x, int):
        return str(x)
    return len(x)
```

## Final & ClassVar
```python
from typing import Final, ClassVar

class Config:
    MAX_SIZE: Final[int] = 100  # Cannot be reassigned
    instance_count: ClassVar[int] = 0  # Class variable

    def __init__(self):
        Config.instance_count += 1
```

## Type Guards
```python
from typing import TypeGuard, List, Any

def is_str_list(val: List[Any]) -> TypeGuard[List[str]]:
    return all(isinstance(x, str) for x in val)

items: List[Any] = ["a", "b", "c"]
if is_str_list(items):
    # items is now List[str]
    upper = [s.upper() for s in items]
```

## Annotated (Metadata)
```python
from typing import Annotated

PositiveInt = Annotated[int, "Must be positive"]
UserId = Annotated[int, "User identifier", "primary_key"]

def validate_age(age: Annotated[int, "0-150"]) -> bool:
    return 0 <= age <= 150
```

## Advanced Generics
```python
from typing import TypeVar, bound, contravariant, covariant

T = TypeVar('T', bound=str)  # T must be str or subclass
T_co = TypeVar('T_co', covariant=True)  # Can use subtype
T_contra = TypeVar('T_contra', contravariant=True)  # Can use supertype

class Reader(Generic[T_co]):
    def read(self) -> T_co: ...

class Writer(Generic[T_contra]):
    def write(self, value: T_contra) -> None: ...
```

## ParamSpec & Concatenate
```python
from typing import ParamSpec, Concatenate, Callable

P = ParamSpec('P')

def add_logging(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def with_context(func: Callable[Concatenate[str, P], T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return func("context", *args, **kwargs)
    return wrapper
```

## Self Type (3.11+)
```python
from typing import Self

class Node:
    def add_child(self, child: Self) -> Self:
        return self

    def clone(self) -> Self:
        return self.__class__()
```

## Type Narrowing
```python
from typing import assert_never

def handle_value(val: int | str) -> str:
    if isinstance(val, int):
        return str(val)
    elif isinstance(val, str):
        return val
    else:
        assert_never(val)  # Exhaustiveness check
```

## Async Types
```python
from typing import Coroutine, AsyncIterator, AsyncGenerator

async def fetch() -> str:
    return "data"

coro: Coroutine[Any, Any, str] = fetch()

async def count() -> AsyncIterator[int]:
    for i in range(10):
        yield i

async def generate() -> AsyncGenerator[int, None]:
    yield 1
    yield 2
```

## Context Managers
```python
from typing import ContextManager, AsyncContextManager
from contextlib import contextmanager

def get_file() -> ContextManager[str]:
    @contextmanager
    def manager():
        yield "file_content"
    return manager()

async_ctx: AsyncContextManager[str]
```

## IO Types
```python
from typing import IO, TextIO, BinaryIO

def read_text(file: TextIO) -> str:
    return file.read()

def read_binary(file: BinaryIO) -> bytes:
    return file.read()

def process_any(file: IO[str]) -> None:
    content = file.read()
```

## Pattern Matching Support (3.10+)
```python
from typing import TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

def process_json(data: JSON) -> None:
    match data:
        case {"type": "user", "name": str(name)}:
            print(f"User: {name}")
        case [*items] if all(isinstance(i, int) for i in items):
            print(f"Integer list: {items}")
        case _:
            print("Other data")
```

## Never & NoReturn
```python
from typing import Never, NoReturn

def raise_error() -> NoReturn:
    raise ValueError("Always raises")

def impossible() -> Never:
    while True:
        pass
```

## Unpack (3.11+)
```python
from typing import TypedDict, Unpack

class MovieKwargs(TypedDict):
    title: str
    year: int
    director: str

def create_movie(**kwargs: Unpack[MovieKwargs]) -> None:
    print(f"{kwargs['title']} ({kwargs['year']})")

create_movie(title="Inception", year=2010, director="Nolan")
```

## Common Patterns
```python
# Factory pattern with generics
T = TypeVar('T')
class Factory(Generic[T]):
    def create(self) -> T: ...

# Singleton with typing
_instance: Optional['Singleton'] = None
class Singleton:
    def __new__(cls) -> 'Singleton':
        global _instance
        if _instance is None:
            _instance = super().__new__(cls)
        return _instance

# Method chaining
class Builder:
    def with_name(self, name: str) -> Self:
        return self

    def with_age(self, age: int) -> Self:
        return self

# Discriminated unions
class Success:
    type: Literal["success"] = "success"
    value: str

class Error:
    type: Literal["error"] = "error"
    message: str

Result = Success | Error
```

## Type Checking Tools
```bash
# Install type checkers
pip install mypy pyright pyre-check

# Run type checking
mypy script.py --strict
pyright script.py
pyre check

# Config example (mypy.ini)
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## Best Practices
1. Start with simple types, add complexity as needed
2. Use `Optional[T]` for nullable values
3. Prefer `Union` over `Any` when possible
4. Create type aliases for complex types
5. Use `Protocol` for duck typing with type safety
6. Add types gradually to existing codebases
7. Configure your IDE for real-time type checking
8. Use `TypedDict` for dictionary schemas
9. Leverage generics for reusable components
10. Run type checkers in CI/CD pipelines