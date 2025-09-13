# Mermaid UML Class Diagram Guide

## Quick Reference for UML Relationships in Mermaid

### Basic Syntax
```mermaid
classDiagram
    class ClassName {
        +public_attribute : Type
        -private_attribute : Type
        #protected_attribute : Type
        +public_method() ReturnType
        -private_method() void
        +abstract_method()* AbstractType
    }
```

## UML Relationship Types & Mermaid Syntax

### 1. **Inheritance/Generalization** (IS-A)
**"Child extends/inherits from Parent"**
```mermaid
classDiagram
    Parent <|-- Child : extends
```
- **Arrow**: `<|--` (hollow triangle pointing to parent)
- **Meaning**: Child IS-A Parent
- **Python**: `class Child(Parent):`

### 2. **Interface Implementation/Realization**
**"Class implements Interface"**
```mermaid
classDiagram
    class IEmployee {
        <<interface>>
        +doWork()*
    }
    IEmployee <|.. Designer : implements
```
- **Arrow**: `<|..` (dashed line with hollow triangle)
- **Meaning**: Designer realizes/implements IEmployee interface
- **Python**: `class Designer(IEmployee):`  where IEmployee is an ABC

### 3. **Association** (HAS-A)
**"Class A has a permanent relationship with Class B"**
```mermaid
classDiagram
    Car --> Engine : has
```
- **Arrow**: `-->` (solid line with arrow)
- **Meaning**: Car HAS an Engine (stored as attribute)
- **Python**: `self.engine = Engine()`

### 4. **Dependency** (USES-A)
**"Class A temporarily uses Class B"**
```mermaid
classDiagram
    EmailService ..> SMTPServer : uses
```
- **Arrow**: `..>` (dashed line with arrow)
- **Meaning**: EmailService USES SMTPServer (parameter/local variable)
- **Python**: `def send(self, smtp_server: SMTPServer):`

### 5. **Aggregation** (Weak HAS-A)
**"Class A has Class B, but B can exist independently"**
```mermaid
classDiagram
    Department o-- Employee : contains
```
- **Arrow**: `o--` (hollow diamond at owner)
- **Meaning**: Department contains Employees (but Employees can exist without Department)
- **Python**: `self.employees = [emp1, emp2]`  # employees exist elsewhere too

### 6. **Composition** (Strong HAS-A)
**"Class A owns Class B, B cannot exist without A"**
```mermaid
classDiagram
    House *-- Room : owns
```
- **Arrow**: `*--` (filled diamond at owner)
- **Meaning**: House owns Rooms (Rooms don't exist without House)
- **Python**: `self.rooms = [Room(), Room()]`  # created by House

## Complete Arrow Reference Table

| Relationship | Mermaid Syntax | Line Style | Arrow Type | Meaning |
|-------------|---------------|------------|------------|---------|
| Inheritance | `<\|--` | Solid | Hollow triangle | IS-A (extends) |
| Implementation | `<\|..` | Dashed | Hollow triangle | Implements interface |
| Association | `-->` | Solid | Open arrow | HAS-A (permanent) |
| Dependency | `..>` | Dashed | Open arrow | USES-A (temporary) |
| Aggregation | `o--` | Solid | Hollow diamond | Weak ownership |
| Composition | `*--` | Solid | Filled diamond | Strong ownership |
| Bidirectional | `<-->` | Solid | Double arrow | Both know each other |
| Note link | `..` | Dashed | None | Links note to class |

## Class Modifiers

```mermaid
classDiagram
    class AbstractClass {
        <<abstract>>
        +abstractMethod()*
    }
    
    class Interface {
        <<interface>>
        +method()*
    }
    
    class Enumeration {
        <<enumeration>>
        RED
        GREEN
        BLUE
    }
    
    class Service {
        <<service>>
        +serve()
    }
```

## Visibility Modifiers

- `+` Public
- `-` Private  
- `#` Protected
- `~` Package/Internal

## Practical Examples

### Example 1: Interface Implementation vs Dependency
```mermaid
classDiagram
    class DataReader {
        <<interface>>
        +read(data)*
    }
    
    class CSVReader {
        +read(data)
    }
    
    class DataProcessor {
        +process(reader, data)
    }
    
    %% CSVReader IMPLEMENTS DataReader (permanent relationship)
    DataReader <|.. CSVReader : implements
    
    %% DataProcessor DEPENDS ON DataReader (temporary use)
    DataProcessor ..> DataReader : uses
```

### Example 2: Association vs Composition vs Aggregation
```mermaid
classDiagram
    class Car {
        -engine: Engine
        -driver: Person
        +start()
    }
    
    class Engine {
        +run()
    }
    
    class Person {
        +drive()
    }
    
    class Wheel {
        +rotate()
    }
    
    %% Car OWNS Engine (composition - engine created with car)
    Car *-- Engine : owns
    
    %% Car HAS 4 Wheels (composition - wheels don't exist without car)
    Car *-- "4" Wheel : has
    
    %% Car ASSOCIATES with Person (driver can change)
    Car --> "0..1" Person : driven by
```

### Example 3: Complete System with All Relationships
```mermaid
classDiagram
    class IEmployee {
        <<interface>>
        +doWork()*
        +getName()* String
    }
    
    class AbstractEmployee {
        <<abstract>>
        #name: String
        #salary: float
        +getName() String
        +doWork()*
    }
    
    class Developer {
        -programmingLanguages: List
        +doWork()
        +code()
    }
    
    class Company {
        -employees: List~IEmployee~
        +hire(employee)
        +createProduct()
    }
    
    class Project {
        -deadline: Date
        +complete()
    }
    
    class Database {
        +connect()
        +query()
    }
    
    %% Inheritance hierarchy
    IEmployee <|.. AbstractEmployee : implements
    AbstractEmployee <|-- Developer : extends
    
    %% Company HAS employees (aggregation - employees can exist without company)
    Company o-- IEmployee : employs
    
    %% Company USES Database (dependency - temporary usage)
    Company ..> Database : queries
    
    %% Developer WORKS ON Project (association)
    Developer --> "*" Project : works on
```

## Cardinality/Multiplicity

Add numbers to show how many instances:
```mermaid
classDiagram
    Teacher "1" --> "*" Student : teaches
    Course "1..*" o-- "3..6" Student : enrolls
```

Common multiplicities:
- `1` - Exactly one
- `0..1` - Zero or one
- `*` or `0..*` - Zero or more
- `1..*` - One or more
- `n` - Exactly n
- `n..m` - Between n and m

## Adding Notes

```mermaid
classDiagram
    class BankAccount {
        -balance: float
        +deposit(amount)
        +withdraw(amount)
    }
    
    note for BankAccount "This class handles all monetary transactions.\nBalance cannot be negative."
```

## Tips for Clear UML Diagrams

1. **Use the right arrow for the relationship**:
   - Implements interface? Use `<|..`
   - Extends class? Use `<|--`
   - Has as attribute? Use `-->`
   - Uses as parameter? Use `..>`

2. **Show important methods and attributes**:
   - Don't show every getter/setter
   - Focus on key behaviors
   - Show attributes that represent relationships

3. **Use stereotypes to clarify**:
   - `<<interface>>` for interfaces
   - `<<abstract>>` for abstract classes
   - `<<enumeration>>` for enums

4. **Add notes for complex logic**:
   - Explain invariants
   - Document design decisions
   - Clarify multiplicities

## Common Mistakes to Avoid

❌ **Wrong**: Using inheritance arrow for interface implementation
```mermaid
classDiagram
    IEmployee <|-- Developer
```

✅ **Correct**: Using realization arrow for interface implementation
```mermaid
classDiagram
    IEmployee <|.. Developer
```

❌ **Wrong**: Using association for temporary usage
```mermaid
classDiagram
    Service --> Database
```

✅ **Correct**: Using dependency for temporary usage
```mermaid
classDiagram
    Service ..> Database
```

## Python to UML Mapping

| Python Code | UML Relationship | Mermaid |
|------------|-----------------|---------|
| `class Child(Parent):` | Inheritance | `Parent <\|-- Child` |
| `class Impl(ABC):` | Implementation | `ABC <\|.. Impl` |
| `self.attr = OtherClass()` | Association/Composition | `Class --> OtherClass` or `Class *-- OtherClass` |
| `def method(self, param: OtherClass):` | Dependency | `Class ..> OtherClass` |
| `self.items = external_items` | Aggregation | `Class o-- Item` |