# Factory Pattern vs Strategy Pattern: A Side-by-Side Comparison

## The Fundamental Difference

| Aspect | Factory Pattern | Strategy Pattern |
|--------|----------------|------------------|
| **Core Question** | "What object should I create?" | "How should this object behave?" |
| **Purpose** | Object creation | Behavior selection |
| **When Decided** | At creation time | Can change at runtime |
| **Result** | Different objects | Same object, different behavior |
| **Flexibility** | Need new object to change type | Can swap behavior on existing object |

## Conceptual Visualization

```
Factory Pattern:
Request → Factory → Creates → Different Objects
         "I need a vehicle"  → 🚗 Car Object
                             → 🏍️ Bike Object
                             → 🚌 Bus Object

Strategy Pattern:
Object → Has Strategy → Executes → Different Behaviors
Navigator object → Car Strategy    → Highway routing
                → Walk Strategy    → Sidewalk routing  
                → Bike Strategy    → Bike lane routing
(Same navigator, different behaviors)
```

## Side-by-Side Examples

### Example 1: Game Character System

#### Problem: Handle different character types with different abilities

#### Factory Pattern Approach
```python
from abc import ABC, abstractmethod

# Factory Pattern: Creates different character objects
class Character(ABC):
    @abstractmethod
    def attack(self):
        pass
    
    @abstractmethod
    def get_stats(self):
        pass

class Warrior(Character):
    def __init__(self, name):
        self.name = name
        self.health = 150
        self.damage = 20
        
    def attack(self):
        return f"{self.name} swings sword for {self.damage} damage!"
    
    def get_stats(self):
        return f"Warrior {self.name}: HP={self.health}, DMG={self.damage}"

class Mage(Character):
    def __init__(self, name):
        self.name = name
        self.health = 80
        self.damage = 35
        self.mana = 100
        
    def attack(self):
        return f"{self.name} casts fireball for {self.damage} damage!"
    
    def get_stats(self):
        return f"Mage {self.name}: HP={self.health}, DMG={self.damage}, Mana={self.mana}"

class Archer(Character):
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.damage = 25
        self.arrows = 30
        
    def attack(self):
        return f"{self.name} shoots arrow for {self.damage} damage!"
    
    def get_stats(self):
        return f"Archer {self.name}: HP={self.health}, DMG={self.damage}, Arrows={self.arrows}"

class CharacterFactory:
    """Factory creates different character objects"""
    @staticmethod
    def create_character(char_type, name):
        if char_type == "warrior":
            return Warrior(name)
        elif char_type == "mage":
            return Mage(name)
        elif char_type == "archer":
            return Archer(name)
        else:
            raise ValueError(f"Unknown character type: {char_type}")

# Usage
factory = CharacterFactory()
hero1 = factory.create_character("warrior", "Conan")
hero2 = factory.create_character("mage", "Gandalf")

print(hero1.get_stats())  # Warrior object
print(hero2.get_stats())  # Mage object
print(hero1.attack())
print(hero2.attack())

# To change character type, you need a NEW object
# hero1 cannot become a mage, you'd need to create a new character
```

#### Strategy Pattern Approach
```python
from abc import ABC, abstractmethod

# Strategy Pattern: Same character, different combat strategies
class CombatStrategy(ABC):
    @abstractmethod
    def attack(self, character_name, base_damage):
        pass
    
    @abstractmethod
    def get_description(self):
        pass

class SwordStrategy(CombatStrategy):
    def attack(self, character_name, base_damage):
        damage = base_damage * 1.0
        return f"{character_name} swings sword for {damage} damage!"
    
    def get_description(self):
        return "Melee combat with sword"

class MagicStrategy(CombatStrategy):
    def attack(self, character_name, base_damage):
        damage = base_damage * 1.5  # Magic multiplier
        return f"{character_name} casts fireball for {damage} damage!"
    
    def get_description(self):
        return "Ranged magic attacks"

class BowStrategy(CombatStrategy):
    def attack(self, character_name, base_damage):
        damage = base_damage * 1.2
        return f"{character_name} shoots arrow for {damage} damage!"
    
    def get_description(self):
        return "Ranged physical attacks"

class Character:
    """Single character class that can switch combat styles"""
    def __init__(self, name, health=100, base_damage=20):
        self.name = name
        self.health = health
        self.base_damage = base_damage
        self.combat_strategy = SwordStrategy()  # Default strategy
    
    def set_combat_strategy(self, strategy):
        """Switch combat style at runtime"""
        self.combat_strategy = strategy
        print(f"{self.name} switched to {strategy.get_description()}")
    
    def attack(self):
        return self.combat_strategy.attack(self.name, self.base_damage)
    
    def get_stats(self):
        return f"{self.name}: HP={self.health}, Base DMG={self.base_damage}, Style={self.combat_strategy.get_description()}"

# Usage
hero = Character("Aragorn", 120, 25)
print(hero.get_stats())
print(hero.attack())  # Uses sword

# Same character can switch strategies at runtime!
hero.set_combat_strategy(MagicStrategy())
print(hero.attack())  # Now uses magic

hero.set_combat_strategy(BowStrategy())
print(hero.attack())  # Now uses bow

# It's the SAME character object, just different behavior
```

### Example 2: Payment Processing System

#### Factory Pattern Approach
```python
# Factory Pattern: Creates different payment processor objects
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class CreditCardProcessor(PaymentProcessor):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
        self.processor_type = "Credit Card"
    
    def process_payment(self, amount):
        # Credit card specific logic
        return f"Processing ${amount} via Credit Card ending in {self.card_number[-4:]}"

class PayPalProcessor(PaymentProcessor):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.processor_type = "PayPal"
    
    def process_payment(self, amount):
        # PayPal specific logic
        return f"Processing ${amount} via PayPal account {self.email}"

class CryptoProcessor(PaymentProcessor):
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.processor_type = "Cryptocurrency"
    
    def process_payment(self, amount):
        # Crypto specific logic
        return f"Processing ${amount} via crypto wallet {self.wallet_address[:8]}..."

class PaymentProcessorFactory:
    @staticmethod
    def create_processor(payment_type, **kwargs):
        if payment_type == "credit_card":
            return CreditCardProcessor(kwargs['card_number'], kwargs['cvv'])
        elif payment_type == "paypal":
            return PayPalProcessor(kwargs['email'], kwargs['password'])
        elif payment_type == "crypto":
            return CryptoProcessor(kwargs['wallet_address'])
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")

# Usage: Different processor objects for different payment types
factory = PaymentProcessorFactory()
processor1 = factory.create_processor("credit_card", card_number="1234567812345678", cvv="123")
processor2 = factory.create_processor("paypal", email="user@example.com", password="secret")

print(processor1.process_payment(100))  # Credit card processor object
print(processor2.process_payment(50))   # PayPal processor object
```

#### Strategy Pattern Approach
```python
# Strategy Pattern: Same checkout system, different payment strategies
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardStrategy(PaymentStrategy):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def pay(self, amount):
        return f"Paid ${amount} using Credit Card ending in {self.card_number[-4:]}"

class PayPalStrategy(PaymentStrategy):
    def __init__(self, email):
        self.email = email
    
    def pay(self, amount):
        return f"Paid ${amount} using PayPal account {self.email}"

class CryptoStrategy(PaymentStrategy):
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
    
    def pay(self, amount):
        btc_amount = amount / 50000  # Convert to BTC
        return f"Paid {btc_amount:.6f} BTC from wallet {self.wallet_address[:8]}..."

class ShoppingCart:
    """Single checkout system that can use different payment methods"""
    def __init__(self):
        self.items = []
        self.payment_strategy = None
    
    def add_item(self, item, price):
        self.items.append({"item": item, "price": price})
    
    def set_payment_strategy(self, strategy):
        """Change payment method at checkout"""
        self.payment_strategy = strategy
    
    def checkout(self):
        total = sum(item["price"] for item in self.items)
        if not self.payment_strategy:
            return "No payment method selected!"
        
        print(f"Cart total: ${total}")
        return self.payment_strategy.pay(total)

# Usage: Same cart, different payment strategies
cart = ShoppingCart()
cart.add_item("Laptop", 1200)
cart.add_item("Mouse", 50)

# Customer chooses credit card
cart.set_payment_strategy(CreditCardStrategy("1234567812345678", "123"))
print(cart.checkout())

# Same cart, customer changes mind and uses PayPal
cart.set_payment_strategy(PayPalStrategy("user@example.com"))
print(cart.checkout())
```

### Example 3: Notification System

#### Both Patterns Combined
```python
# Sometimes you need BOTH patterns working together!

# Strategy Pattern: Different ways to send notifications
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class EmailStrategy(NotificationStrategy):
    def send(self, message, recipient):
        return f"📧 Email sent to {recipient}: {message}"

class SMSStrategy(NotificationStrategy):
    def send(self, message, recipient):
        return f"📱 SMS sent to {recipient}: {message}"

class PushStrategy(NotificationStrategy):
    def send(self, message, recipient):
        return f"🔔 Push notification to {recipient}: {message}"

# Factory Pattern: Creates appropriate strategy based on user preferences
class NotificationStrategyFactory:
    @staticmethod
    def create_strategy(user_preference):
        """Factory creates the right strategy based on user settings"""
        if user_preference == "email":
            return EmailStrategy()
        elif user_preference == "sms":
            return SMSStrategy()
        elif user_preference == "push":
            return PushStrategy()
        else:
            return EmailStrategy()  # Default

# Context class uses strategies
class NotificationService:
    def __init__(self):
        self.strategy = None
        self.factory = NotificationStrategyFactory()
    
    def setup_for_user(self, user_preference):
        """Factory creates strategy based on user preference"""
        self.strategy = self.factory.create_strategy(user_preference)
    
    def send_notification(self, message, recipient):
        if not self.strategy:
            raise ValueError("No notification strategy set!")
        return self.strategy.send(message, recipient)
    
    def change_strategy(self, new_strategy):
        """Can also manually change strategy"""
        self.strategy = new_strategy

# Usage: Factory and Strategy working together
service = NotificationService()

# Factory creates strategy based on user preference
service.setup_for_user("email")
print(service.send_notification("Your order shipped!", "john@example.com"))

# User changes preference
service.setup_for_user("sms")
print(service.send_notification("Delivery tomorrow", "+1234567890"))

# Or manually override with specific strategy
service.change_strategy(PushStrategy())
print(service.send_notification("Package delivered!", "user123"))
```

## Key Decision Points

### When to Use Factory Pattern

✅ **Use Factory when:**
- You don't know which class to instantiate until runtime
- You want to centralize complex object creation logic
- Objects have different interfaces or vastly different implementations
- You're dealing with object families (Abstract Factory)
- The object type won't change after creation

❌ **Don't use Factory when:**
- You only have one or two simple types
- Object creation is straightforward
- You need to change behavior after creation

### When to Use Strategy Pattern

✅ **Use Strategy when:**
- You have multiple algorithms for the same task
- You want to switch algorithms at runtime
- You want to eliminate conditional statements for behavior selection
- Algorithms are interchangeable through a common interface
- You need to isolate algorithm implementation details

❌ **Don't use Strategy when:**
- You only have one algorithm
- The algorithm never changes
- The variations are simple enough for a single method

## Memory Tricks

### Factory Pattern
Think: **"Factory Assembly Line"**
- Input: Raw materials (parameters)
- Output: Finished products (different objects)
- Once built, a car doesn't transform into a motorcycle

### Strategy Pattern
Think: **"Swiss Army Knife"**
- Same tool (object)
- Different attachments (strategies)
- Switch between knife, scissors, screwdriver as needed

## Common Pitfalls

### Factory Pattern Pitfalls
1. **Over-engineering**: Creating factories for simple objects
2. **Type explosion**: Too many product classes
3. **Rigid hierarchies**: Hard to add new types without modifying factory

### Strategy Pattern Pitfalls
1. **Too many strategies**: Creating strategies for trivial variations
2. **Overhead**: Extra classes for simple if/else logic
3. **Client complexity**: Client needs to know about strategies

## Combining Both Patterns

Real applications often use both patterns together:

```python
# E-commerce System Example
class OrderService:
    def __init__(self):
        # Factory creates appropriate objects
        self.payment_factory = PaymentProcessorFactory()
        self.shipping_factory = ShippingProviderFactory()
        
        # Strategies define behaviors
        self.pricing_strategy = None  # Regular, Premium, Sale pricing
        self.tax_strategy = None      # Different tax calculations
    
    def process_order(self, order):
        # Factory creates payment processor based on payment method
        payment = self.payment_factory.create(order.payment_type)
        
        # Strategy calculates price based on current promotion
        total = self.pricing_strategy.calculate(order.items)
        
        # Process payment using created processor
        payment.charge(total)
        
        # Factory creates shipping provider
        shipper = self.shipping_factory.create(order.shipping_type)
        shipper.ship(order)
```

## Summary

| Pattern | Factory | Strategy |
|---------|---------|----------|
| **Focus** | Object Creation | Algorithm Selection |
| **Question** | "What to create?" | "How to do it?" |
| **Flexibility** | Static after creation | Dynamic at runtime |
| **Use Case** | Different types of objects | Different ways to perform task |
| **Example** | Create PDF vs Word document | Export document as PDF vs Word |

Remember: **Factory creates objects, Strategy defines behaviors**. They solve different problems and can work together beautifully!