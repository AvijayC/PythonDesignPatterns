# Strategy Pattern: Navigation App Example

## The Problem: Growing Complexity

Imagine you're building a navigation app that started simple but grew complex over time:

### Initial Situation
```
NavigationApp
├── Beautiful Map Display
└── Route Planning (Car only)
```

### After Multiple Updates
```
NavigationApp (becoming a monolith!)
├── Beautiful Map Display
├── Car Route Planning
├── Walking Route Planning  
├── Public Transport Planning
├── Cycling Route Planning
└── Tourist Attraction Routes
```

### Why This Is Problematic

1. **Class Bloat**: The main Navigator class doubles in size with each new routing algorithm
2. **High Risk of Bugs**: Changing one algorithm might break others since they're all in the same class
3. **Merge Conflicts**: Multiple developers working on different routing algorithms constantly conflict
4. **Violation of Single Responsibility**: One class is doing too many different things
5. **Hard to Test**: You can't test routing algorithms in isolation

## The Solution: Strategy Pattern

The Strategy Pattern separates the "what" from the "how":
- **What**: The Navigator needs to calculate a route
- **How**: Different algorithms (car, walk, bike, etc.) calculate routes differently

### Core Components

1. **Strategy Interface**: Defines a common method all strategies must implement
2. **Concrete Strategies**: Individual classes for each routing algorithm
3. **Context (Navigator)**: Maintains a reference to a strategy and delegates work to it
4. **Client**: Selects which strategy to use

## Implementation in Python

### 1. Define the Strategy Interface

```python
from abc import ABC, abstractmethod
from typing import List, Tuple

class RouteStrategy(ABC):
    """Abstract base class for all routing strategies"""
    
    @abstractmethod
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Calculate a route from origin to destination
        Returns a list of waypoints (latitude, longitude tuples)
        """
        pass
```

### 2. Implement Concrete Strategies

```python
class CarRouteStrategy(RouteStrategy):
    """Strategy for calculating driving routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"Calculating fastest car route from {origin} to {destination}")
        # Prioritize highways, avoid pedestrian zones
        # Complex algorithm here...
        return [origin, (origin[0] + 0.1, origin[1]), destination]

class WalkingRouteStrategy(RouteStrategy):
    """Strategy for calculating walking routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"Calculating pedestrian route from {origin} to {destination}")
        # Use sidewalks, parks, pedestrian zones
        # Different algorithm here...
        return [origin, (origin[0], origin[1] + 0.05), destination]

class PublicTransportStrategy(RouteStrategy):
    """Strategy for calculating public transport routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"Finding public transport route from {origin} to {destination}")
        # Connect to transit API, find stops
        # Another different algorithm...
        return [origin, (origin[0] + 0.05, origin[1] + 0.05), destination]

class CyclingRouteStrategy(RouteStrategy):
    """Strategy for calculating cycling routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"Calculating bike-friendly route from {origin} to {destination}")
        # Prefer bike lanes, avoid steep hills
        return [origin, (origin[0] - 0.05, origin[1] + 0.1), destination]
```

### 3. Create the Context Class (Navigator)

```python
class Navigator:
    """
    The context class that uses routing strategies
    """
    
    def __init__(self, strategy: RouteStrategy = None):
        """Initialize with an optional default strategy"""
        self._strategy = strategy or CarRouteStrategy()
        self._current_route = []
    
    def set_strategy(self, strategy: RouteStrategy):
        """
        Change the routing strategy at runtime
        This is called when user clicks different transport mode buttons
        """
        print(f"Switching to {strategy.__class__.__name__}")
        self._strategy = strategy
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]):
        """
        Delegate route calculation to the current strategy
        """
        if not self._strategy:
            raise ValueError("No routing strategy set!")
        
        self._current_route = self._strategy.build_route(origin, destination)
        self._display_route()
    
    def _display_route(self):
        """Render the route on the map"""
        print(f"Displaying route with {len(self._current_route)} waypoints")
        for i, point in enumerate(self._current_route):
            print(f"  Waypoint {i + 1}: {point}")
```

### 4. Client Code (How It's Used)

```python
def main():
    # Create navigator with default car strategy
    navigator = Navigator()
    
    origin = (40.7128, -74.0060)      # New York City
    destination = (40.7580, -73.9855)  # Times Square
    
    # User wants driving directions
    print("=== User selects CAR mode ===")
    navigator.build_route(origin, destination)
    
    # User switches to walking mode
    print("\n=== User selects WALKING mode ===")
    navigator.set_strategy(WalkingRouteStrategy())
    navigator.build_route(origin, destination)
    
    # User wants to try public transport
    print("\n=== User selects PUBLIC TRANSPORT mode ===")
    navigator.set_strategy(PublicTransportStrategy())
    navigator.build_route(origin, destination)
    
    # User switches to cycling
    print("\n=== User selects CYCLING mode ===")
    navigator.set_strategy(CyclingRouteStrategy())
    navigator.build_route(origin, destination)

if __name__ == "__main__":
    main()
```

### Output Example
```
=== User selects CAR mode ===
Calculating fastest car route from (40.7128, -74.006) to (40.758, -73.9855)
Displaying route with 3 waypoints
  Waypoint 1: (40.7128, -74.006)
  Waypoint 2: (40.8128, -74.006)
  Waypoint 3: (40.758, -73.9855)

=== User selects WALKING mode ===
Switching to WalkingRouteStrategy
Calculating pedestrian route from (40.7128, -74.006) to (40.758, -73.9855)
Displaying route with 3 waypoints
  Waypoint 1: (40.7128, -74.006)
  Waypoint 2: (40.7128, -73.956)
  Waypoint 3: (40.758, -73.9855)
```

## Real-World Benefits

### 1. Easy to Add New Strategies
Want to add a "Tourist Route" strategy? Just create a new class:

```python
class TouristRouteStrategy(RouteStrategy):
    """Strategy for scenic routes through tourist attractions"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"Finding scenic route with tourist attractions")
        # Include monuments, museums, photo spots
        return [origin, (40.7484, -73.9857), (40.7614, -73.9776), destination]
```

### 2. Testability
Each strategy can be tested independently:

```python
def test_car_route_avoids_pedestrian_zones():
    strategy = CarRouteStrategy()
    route = strategy.build_route((0, 0), (1, 1))
    # Assert route doesn't go through pedestrian zones
    assert pedestrian_zone not in route

def test_walking_route_uses_sidewalks():
    strategy = WalkingRouteStrategy()
    route = strategy.build_route((0, 0), (1, 1))
    # Assert route uses sidewalks
    assert all(has_sidewalk(segment) for segment in route)
```

### 3. Open/Closed Principle
The Navigator class is:
- **Open for extension**: Add new strategies without modifying Navigator
- **Closed for modification**: Navigator code doesn't change when adding strategies

### 4. Team Collaboration
Different developers can work on different strategies without conflicts:
- Alice works on `CarRouteStrategy`
- Bob works on `PublicTransportStrategy`
- No merge conflicts!

## When to Use Strategy Pattern

✅ **Use Strategy When:**
- You have multiple ways to perform a task
- You want to switch between algorithms at runtime
- You have a class with many conditional statements selecting behavior
- Related classes differ only in their behavior

❌ **Don't Use Strategy When:**
- You only have one or two algorithms that rarely change
- The algorithms are very simple
- The client shouldn't be aware of different strategies

## Common Real-World Examples

1. **Payment Processing**: Different payment methods (Credit Card, PayPal, Bitcoin)
2. **Data Compression**: Different compression algorithms (ZIP, RAR, 7z)
3. **Sorting Algorithms**: Different sorting strategies (QuickSort, MergeSort, BubbleSort)
4. **Authentication**: Different auth methods (OAuth, JWT, Session-based)
5. **Pricing Strategies**: Different discount calculations (Percentage, Fixed, BOGO)

## Key Takeaways

1. **Separation of Concerns**: Each strategy handles one specific algorithm
2. **Runtime Flexibility**: Switch strategies without restarting the application
3. **Clean Code**: Eliminates large conditional blocks
4. **Maintainability**: Changes to one strategy don't affect others
5. **Testability**: Each strategy can be unit tested in isolation

The Strategy Pattern transforms a monolithic, hard-to-maintain class into a flexible, extensible system where adding new behaviors is as simple as creating a new strategy class!