#!/usr/bin/env python3
"""
Strategy Pattern Example: Navigation App
A practical demonstration of how the Strategy Pattern solves real-world problems
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import random


class RouteStrategy(ABC):
    """Abstract base class defining the interface for all routing strategies"""
    
    @abstractmethod
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Calculate a route from origin to destination"""
        pass
    
    @abstractmethod
    def get_estimated_time(self, distance: float) -> float:
        """Calculate estimated travel time based on distance"""
        pass


class CarRouteStrategy(RouteStrategy):
    """Strategy for calculating driving routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"🚗 Calculating fastest car route...")
        print(f"   - Prioritizing highways")
        print(f"   - Avoiding pedestrian zones")
        print(f"   - Checking traffic conditions")
        
        route = [
            origin,
            (origin[0] + 0.1, origin[1]),
            (origin[0] + 0.1, origin[1] + 0.1),
            destination
        ]
        return route
    
    def get_estimated_time(self, distance: float) -> float:
        speed_kmh = 60
        return (distance / speed_kmh) * 60


class WalkingRouteStrategy(RouteStrategy):
    """Strategy for calculating walking routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"🚶 Calculating pedestrian route...")
        print(f"   - Using sidewalks and crosswalks")
        print(f"   - Including parks and pedestrian zones")
        print(f"   - Finding safest path")
        
        route = [
            origin,
            (origin[0], origin[1] + 0.05),
            (origin[0] + 0.05, origin[1] + 0.05),
            destination
        ]
        return route
    
    def get_estimated_time(self, distance: float) -> float:
        speed_kmh = 5
        return (distance / speed_kmh) * 60


class PublicTransportStrategy(RouteStrategy):
    """Strategy for calculating public transport routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"🚌 Finding public transport route...")
        print(f"   - Locating nearest bus/metro stops")
        print(f"   - Checking schedules")
        print(f"   - Minimizing transfers")
        
        route = [
            origin,
            (origin[0] + 0.02, origin[1]),
            (origin[0] + 0.05, origin[1] + 0.08),
            (destination[0] - 0.01, destination[1]),
            destination
        ]
        return route
    
    def get_estimated_time(self, distance: float) -> float:
        speed_kmh = 30
        wait_time = 10
        return (distance / speed_kmh) * 60 + wait_time


class CyclingRouteStrategy(RouteStrategy):
    """Strategy for calculating cycling routes"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"🚴 Calculating bike-friendly route...")
        print(f"   - Preferring bike lanes")
        print(f"   - Avoiding steep hills")
        print(f"   - Considering bike parking")
        
        route = [
            origin,
            (origin[0] - 0.02, origin[1] + 0.05),
            (origin[0] + 0.03, origin[1] + 0.08),
            destination
        ]
        return route
    
    def get_estimated_time(self, distance: float) -> float:
        speed_kmh = 15
        return (distance / speed_kmh) * 60


class TouristRouteStrategy(RouteStrategy):
    """Strategy for scenic routes through tourist attractions"""
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        print(f"📸 Finding scenic tourist route...")
        print(f"   - Including major landmarks")
        print(f"   - Adding photo opportunities")
        print(f"   - Passing through historic districts")
        
        route = [
            origin,
            (origin[0] + 0.03, origin[1] + 0.02),
            (40.7484, -73.9857),
            (40.7614, -73.9776),
            (destination[0] - 0.02, destination[1] + 0.01),
            destination
        ]
        return route
    
    def get_estimated_time(self, distance: float) -> float:
        speed_kmh = 4
        photo_stops = 45
        return (distance / speed_kmh) * 60 + photo_stops


class Navigator:
    """
    The context class that uses routing strategies.
    This is what the UI interacts with.
    """
    
    def __init__(self, strategy: RouteStrategy = None):
        """Initialize with an optional default strategy"""
        self._strategy = strategy or CarRouteStrategy()
        self._current_route = []
        self._origin = None
        self._destination = None
    
    def set_strategy(self, strategy: RouteStrategy):
        """Change the routing strategy at runtime"""
        old_strategy = self._strategy.__class__.__name__
        new_strategy = strategy.__class__.__name__
        print(f"\n📍 Transport mode changed: {old_strategy} → {new_strategy}")
        self._strategy = strategy
        
        if self._origin and self._destination:
            print("   Recalculating route with new mode...")
    
    def build_route(self, origin: Tuple[float, float], 
                   destination: Tuple[float, float]):
        """Delegate route calculation to the current strategy"""
        if not self._strategy:
            raise ValueError("No routing strategy set!")
        
        self._origin = origin
        self._destination = destination
        
        print(f"\n📍 Route Request:")
        print(f"   From: {self._format_location(origin)}")
        print(f"   To: {self._format_location(destination)}")
        
        self._current_route = self._strategy.build_route(origin, destination)
        self._display_route()
    
    def _format_location(self, coords: Tuple[float, float]) -> str:
        """Format coordinates as a readable location"""
        return f"({coords[0]:.4f}, {coords[1]:.4f})"
    
    def _calculate_distance(self) -> float:
        """Calculate approximate route distance"""
        if not self._current_route:
            return 0
        
        distance = 0
        for i in range(len(self._current_route) - 1):
            lat_diff = self._current_route[i+1][0] - self._current_route[i][0]
            lon_diff = self._current_route[i+1][1] - self._current_route[i][1]
            distance += (lat_diff**2 + lon_diff**2)**0.5
        
        return distance * 111
    
    def _display_route(self):
        """Render the route information"""
        distance = self._calculate_distance()
        time = self._strategy.get_estimated_time(distance)
        
        print(f"\n✅ Route Calculated:")
        print(f"   Distance: {distance:.1f} km")
        print(f"   Estimated time: {time:.0f} minutes")
        print(f"   Waypoints: {len(self._current_route)}")
        
        print("\n   Route preview:")
        for i, point in enumerate(self._current_route):
            if i == 0:
                print(f"   📍 Start: {self._format_location(point)}")
            elif i == len(self._current_route) - 1:
                print(f"   🎯 End: {self._format_location(point)}")
            else:
                print(f"   · Via: {self._format_location(point)}")


class NavigationApp:
    """
    Simulates the UI of the navigation app.
    This would be your buttons and user interface in a real app.
    """
    
    def __init__(self):
        self.navigator = Navigator()
        self.strategies = {
            '1': ('Car', CarRouteStrategy()),
            '2': ('Walking', WalkingRouteStrategy()),
            '3': ('Public Transport', PublicTransportStrategy()),
            '4': ('Cycling', CyclingRouteStrategy()),
            '5': ('Tourist', TouristRouteStrategy()),
        }
    
    def show_menu(self):
        """Display transport mode options"""
        print("\n" + "="*60)
        print("NAVIGATION APP - Select Transport Mode")
        print("="*60)
        for key, (name, _) in self.strategies.items():
            print(f"  [{key}] {name}")
        print("  [Q] Quit")
        print("-"*60)
    
    def run(self):
        """Main application loop"""
        print("\n🗺️  Welcome to Navigation App!")
        print("Using Strategy Pattern for flexible route planning")
        
        origin = (40.7128, -74.0060)
        destination = (40.7580, -73.9855)
        
        while True:
            self.show_menu()
            choice = input("Select transport mode: ").strip().upper()
            
            if choice == 'Q':
                print("\n👋 Thanks for using Navigation App!")
                break
            
            if choice in self.strategies:
                name, strategy = self.strategies[choice]
                self.navigator.set_strategy(strategy)
                self.navigator.build_route(origin, destination)
            else:
                print("❌ Invalid choice. Please try again.")


def demonstrate_strategy_benefits():
    """Show the benefits of using Strategy Pattern"""
    print("\n" + "="*60)
    print("STRATEGY PATTERN BENEFITS DEMONSTRATION")
    print("="*60)
    
    print("\n1️⃣  Runtime Strategy Switching:")
    print("   The same navigator instance can switch between strategies")
    
    nav = Navigator()
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    nav.set_strategy(CarRouteStrategy())
    nav.build_route(origin, destination)
    
    nav.set_strategy(WalkingRouteStrategy())
    nav.build_route(origin, destination)
    
    print("\n2️⃣  Easy to Add New Strategies:")
    print("   Just create a new class implementing RouteStrategy")
    print("   No need to modify Navigator or other strategies!")
    
    print("\n3️⃣  Each Strategy is Independent:")
    print("   - CarRouteStrategy can be tested separately")
    print("   - WalkingRouteStrategy can be developed by another team")
    print("   - PublicTransportStrategy can use external APIs")
    
    print("\n4️⃣  Clean Separation of Concerns:")
    print("   - Navigator handles UI and display")
    print("   - Strategies handle route calculation")
    print("   - Client code just selects strategies")


def main():
    """Main entry point"""
    print("\n🚀 Strategy Pattern Demo: Navigation App")
    print("-" * 60)
    
    choice = input("Run [I]nteractive app or [D]emonstration? (I/D): ").strip().upper()
    
    if choice == 'D':
        demonstrate_strategy_benefits()
    else:
        app = NavigationApp()
        app.run()


if __name__ == "__main__":
    main()