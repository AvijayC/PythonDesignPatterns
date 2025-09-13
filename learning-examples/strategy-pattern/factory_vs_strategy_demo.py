#!/usr/bin/env python3
"""
Factory vs Strategy Pattern - Interactive Demo
Shows the difference between creating objects (Factory) and changing behavior (Strategy)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import random


print("=" * 70)
print("FACTORY PATTERN VS STRATEGY PATTERN - INTERACTIVE DEMO")
print("=" * 70)


class DemoSection:
    """Helper class for demo organization"""
    @staticmethod
    def show_section(title):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)


# ============================================================================
# PART 1: GAME CHARACTER SYSTEM - COMPARING BOTH APPROACHES
# ============================================================================

class DemoSection1:
    """Game Character System demonstrating both patterns"""
    
    @staticmethod
    def run():
        DemoSection.show_section("PART 1: GAME CHARACTER SYSTEM")
        print("\nProblem: Handle different character types with different abilities")
        print("-" * 70)
        
        # Factory Pattern Demo
        print("\n🏭 FACTORY PATTERN APPROACH:")
        print("Creating different character objects")
        print("-" * 40)
        
        class Character(ABC):
            @abstractmethod
            def attack(self): pass
            @abstractmethod
            def special_ability(self): pass
        
        class Warrior(Character):
            def __init__(self, name):
                self.name = name
                self.health = 150
                self.character_type = "Warrior"
            
            def attack(self):
                return f"⚔️  {self.name} swings mighty sword!"
            
            def special_ability(self):
                return f"🛡️  {self.name} raises shield (damage reduced by 50%)"
        
        class Mage(Character):
            def __init__(self, name):
                self.name = name
                self.health = 80
                self.character_type = "Mage"
                self.mana = 100
            
            def attack(self):
                return f"🔮 {self.name} casts arcane bolt!"
            
            def special_ability(self):
                return f"✨ {self.name} teleports away (avoids all damage)"
        
        class CharacterFactory:
            @staticmethod
            def create_character(char_type, name):
                if char_type == "warrior":
                    return Warrior(name)
                elif char_type == "mage":
                    return Mage(name)
        
        # Factory Pattern Usage
        factory = CharacterFactory()
        hero1 = factory.create_character("warrior", "Conan")
        hero2 = factory.create_character("mage", "Merlin")
        
        print(f"Created: {hero1.character_type} named {hero1.name}")
        print(f"  {hero1.attack()}")
        print(f"  {hero1.special_ability()}")
        
        print(f"\nCreated: {hero2.character_type} named {hero2.name}")
        print(f"  {hero2.attack()}")
        print(f"  {hero2.special_ability()}")
        
        print("\n❌ Limitation: To change Conan to a mage, we need a NEW object")
        print("   hero1 is forever a Warrior object")
        
        # Strategy Pattern Demo
        print("\n\n🎯 STRATEGY PATTERN APPROACH:")
        print("Same character, switchable combat styles")
        print("-" * 40)
        
        class CombatStyle(ABC):
            @abstractmethod
            def execute_attack(self, character_name): pass
            @abstractmethod
            def get_style_name(self): pass
        
        class SwordStyle(CombatStyle):
            def execute_attack(self, character_name):
                return f"⚔️  {character_name} performs sword combo!"
            def get_style_name(self):
                return "Sword Combat"
        
        class MagicStyle(CombatStyle):
            def execute_attack(self, character_name):
                return f"🔮 {character_name} channels magical energy!"
            def get_style_name(self):
                return "Magic Combat"
        
        class StealthStyle(CombatStyle):
            def execute_attack(self, character_name):
                return f"🗡️  {character_name} strikes from shadows!"
            def get_style_name(self):
                return "Stealth Combat"
        
        class AdaptiveCharacter:
            def __init__(self, name):
                self.name = name
                self.combat_style = SwordStyle()
            
            def switch_style(self, new_style):
                old_style = self.combat_style.get_style_name()
                self.combat_style = new_style
                return f"🔄 {self.name} switched from {old_style} to {new_style.get_style_name()}"
            
            def attack(self):
                return self.combat_style.execute_attack(self.name)
        
        # Strategy Pattern Usage
        hero = AdaptiveCharacter("Aragorn")
        print(f"Created: Adaptive character named {hero.name}")
        print(f"  {hero.attack()}")
        
        print(f"\n{hero.switch_style(MagicStyle())}")
        print(f"  {hero.attack()}")
        
        print(f"\n{hero.switch_style(StealthStyle())}")
        print(f"  {hero.attack()}")
        
        print("\n✅ Advantage: Same character object can change behavior at runtime!")


# ============================================================================
# PART 2: DOCUMENT SYSTEM - SHOWING THE KEY DIFFERENCE
# ============================================================================

class DemoSection2:
    """Document system showing creation vs behavior"""
    
    @staticmethod
    def run():
        DemoSection.show_section("PART 2: DOCUMENT SYSTEM")
        print("\nShowing the fundamental difference between the patterns")
        print("-" * 70)
        
        # Factory: Creating different document types
        print("\n🏭 FACTORY: Creating Different Document Objects")
        print("-" * 40)
        
        class Document(ABC):
            @abstractmethod
            def open(self): pass
            @abstractmethod
            def get_type(self): pass
        
        class PDFDocument(Document):
            def __init__(self, title):
                self.title = title
                self.doc_type = "PDF"
            
            def open(self):
                return f"📕 Opening PDF: {self.title}.pdf in Adobe Reader"
            
            def get_type(self):
                return self.doc_type
        
        class WordDocument(Document):
            def __init__(self, title):
                self.title = title
                self.doc_type = "Word"
            
            def open(self):
                return f"📘 Opening Word: {self.title}.docx in Microsoft Word"
            
            def get_type(self):
                return self.doc_type
        
        class DocumentFactory:
            @staticmethod
            def create_document(doc_type, title):
                if doc_type == "pdf":
                    return PDFDocument(title)
                elif doc_type == "word":
                    return WordDocument(title)
        
        factory = DocumentFactory()
        doc1 = factory.create_document("pdf", "Report")
        doc2 = factory.create_document("word", "Letter")
        
        print(f"Factory created: {doc1.get_type()} document")
        print(f"  {doc1.open()}")
        print(f"\nFactory created: {doc2.get_type()} document")
        print(f"  {doc2.open()}")
        
        # Strategy: Same document, different export methods
        print("\n\n🎯 STRATEGY: Same Document, Different Export Behaviors")
        print("-" * 40)
        
        class ExportStrategy(ABC):
            @abstractmethod
            def export(self, content, filename): pass
        
        class PDFExportStrategy(ExportStrategy):
            def export(self, content, filename):
                return f"💾 Exporting '{content[:20]}...' as {filename}.pdf"
        
        class WordExportStrategy(ExportStrategy):
            def export(self, content, filename):
                return f"💾 Exporting '{content[:20]}...' as {filename}.docx"
        
        class HTMLExportStrategy(ExportStrategy):
            def export(self, content, filename):
                return f"💾 Exporting '{content[:20]}...' as {filename}.html"
        
        class FlexibleDocument:
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
                self.export_strategy = None
            
            def set_export_strategy(self, strategy):
                self.export_strategy = strategy
            
            def export(self):
                if not self.export_strategy:
                    return "❌ No export strategy set!"
                return self.export_strategy.export(self.content, self.filename)
        
        doc = FlexibleDocument("This is my important document content", "mydoc")
        
        print("Created one document with content")
        
        doc.set_export_strategy(PDFExportStrategy())
        print(f"  {doc.export()}")
        
        doc.set_export_strategy(WordExportStrategy())
        print(f"  {doc.export()}")
        
        doc.set_export_strategy(HTMLExportStrategy())
        print(f"  {doc.export()}")
        
        print("\n📝 Key Insight:")
        print("  Factory: Different document OBJECTS (PDF vs Word)")
        print("  Strategy: Same document, different EXPORT methods")


# ============================================================================
# PART 3: COMBINED EXAMPLE - USING BOTH PATTERNS TOGETHER
# ============================================================================

class DemoSection3:
    """E-commerce system using both patterns together"""
    
    @staticmethod
    def run():
        DemoSection.show_section("PART 3: USING BOTH PATTERNS TOGETHER")
        print("\nE-commerce Order Processing System")
        print("-" * 70)
        
        # Strategies for pricing
        class PricingStrategy(ABC):
            @abstractmethod
            def calculate_total(self, items): pass
            @abstractmethod
            def get_description(self): pass
        
        class RegularPricing(PricingStrategy):
            def calculate_total(self, items):
                return sum(item['price'] * item['quantity'] for item in items)
            def get_description(self):
                return "Regular Pricing"
        
        class SalePricing(PricingStrategy):
            def calculate_total(self, items):
                subtotal = sum(item['price'] * item['quantity'] for item in items)
                return subtotal * 0.8  # 20% off
            def get_description(self):
                return "Sale Pricing (20% off)"
        
        class PremiumPricing(PricingStrategy):
            def calculate_total(self, items):
                subtotal = sum(item['price'] * item['quantity'] for item in items)
                return subtotal * 0.85  # 15% off for premium members
            def get_description(self):
                return "Premium Member Pricing (15% off)"
        
        # Factory for creating shipping providers
        class ShippingProvider(ABC):
            @abstractmethod
            def ship(self, order_id): pass
            @abstractmethod
            def get_name(self): pass
        
        class StandardShipping(ShippingProvider):
            def ship(self, order_id):
                return f"📦 Standard shipping (5-7 days) for order #{order_id}"
            def get_name(self):
                return "Standard Shipping"
        
        class ExpressShipping(ShippingProvider):
            def ship(self, order_id):
                return f"🚚 Express shipping (1-2 days) for order #{order_id}"
            def get_name(self):
                return "Express Shipping"
        
        class ShippingFactory:
            @staticmethod
            def create_shipping(shipping_type):
                if shipping_type == "standard":
                    return StandardShipping()
                elif shipping_type == "express":
                    return ExpressShipping()
        
        # Order processor using both patterns
        class OrderProcessor:
            def __init__(self):
                self.pricing_strategy = RegularPricing()
                self.shipping_factory = ShippingFactory()
                self.order_id = random.randint(1000, 9999)
            
            def set_pricing_strategy(self, strategy):
                self.pricing_strategy = strategy
                print(f"  💰 Pricing changed to: {strategy.get_description()}")
            
            def process_order(self, items, shipping_type):
                print(f"\n🛒 Processing Order #{self.order_id}")
                print("-" * 40)
                
                # Strategy Pattern: Calculate price using current strategy
                total = self.pricing_strategy.calculate_total(items)
                print(f"  Items: {len(items)}")
                print(f"  Pricing: {self.pricing_strategy.get_description()}")
                print(f"  Total: ${total:.2f}")
                
                # Factory Pattern: Create appropriate shipping provider
                shipper = self.shipping_factory.create_shipping(shipping_type)
                print(f"  {shipper.ship(self.order_id)}")
                
                return total
        
        # Demo usage
        processor = OrderProcessor()
        
        items = [
            {'name': 'Laptop', 'price': 999.99, 'quantity': 1},
            {'name': 'Mouse', 'price': 49.99, 'quantity': 2},
            {'name': 'Keyboard', 'price': 79.99, 'quantity': 1}
        ]
        
        print("Customer 1: Regular customer, standard shipping")
        processor.process_order(items, "standard")
        
        print("\n\nCustomer 2: Premium member, express shipping")
        processor.set_pricing_strategy(PremiumPricing())
        processor.order_id = random.randint(1000, 9999)
        processor.process_order(items, "express")
        
        print("\n\nCustomer 3: During sale event, standard shipping")
        processor.set_pricing_strategy(SalePricing())
        processor.order_id = random.randint(1000, 9999)
        processor.process_order(items, "standard")
        
        print("\n\n📊 Pattern Usage Summary:")
        print("  • Factory Pattern: Created different shipping providers")
        print("  • Strategy Pattern: Changed pricing calculation method")
        print("  • Both work together in the order processing system!")


# ============================================================================
# INTERACTIVE QUIZ
# ============================================================================

class InteractiveQuiz:
    """Test your understanding of the patterns"""
    
    @staticmethod
    def run():
        DemoSection.show_section("INTERACTIVE QUIZ")
        print("\nTest your understanding of Factory vs Strategy patterns!")
        print("-" * 70)
        
        questions = [
            {
                "question": "You need a system where users can switch between different sorting algorithms at runtime. Which pattern?",
                "answer": "strategy",
                "explanation": "Strategy Pattern - You want to change the BEHAVIOR (how sorting is done) at runtime, not create different sorter objects."
            },
            {
                "question": "You're building a game that creates different types of enemies based on the level difficulty. Which pattern?",
                "answer": "factory",
                "explanation": "Factory Pattern - You need to CREATE different enemy objects (Goblin, Orc, Dragon) based on runtime conditions."
            },
            {
                "question": "Your app needs to support multiple payment methods that users can switch between. Which pattern?",
                "answer": "strategy",
                "explanation": "Strategy Pattern - Same checkout process, different payment BEHAVIORS (how payment is processed)."
            },
            {
                "question": "You need to create different database connection objects based on configuration. Which pattern?",
                "answer": "factory",
                "explanation": "Factory Pattern - You're CREATING different connection objects (MySQL, PostgreSQL, MongoDB) based on config."
            }
        ]
        
        score = 0
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"  {q['question']}")
            answer = input("  Your answer (factory/strategy): ").lower().strip()
            
            if answer == q['answer']:
                print("  ✅ Correct!")
                score += 1
            else:
                print(f"  ❌ Incorrect. The answer is: {q['answer'].title()} Pattern")
            
            print(f"  💡 {q['explanation']}")
        
        print(f"\n\n🏆 Final Score: {score}/{len(questions)}")
        if score == len(questions):
            print("   Perfect! You understand the difference between Factory and Strategy patterns!")
        elif score >= len(questions) // 2:
            print("   Good job! You're getting the hang of it.")
        else:
            print("   Keep practicing! Remember: Factory creates objects, Strategy changes behavior.")


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    """Main demo runner"""
    
    while True:
        print("\n" + "="*70)
        print("  FACTORY vs STRATEGY PATTERN - INTERACTIVE DEMO")
        print("="*70)
        print("\nChoose a demo section:")
        print("  [1] Game Character System (Compare both approaches)")
        print("  [2] Document System (Creation vs Behavior)")
        print("  [3] E-commerce System (Both patterns together)")
        print("  [4] Interactive Quiz")
        print("  [5] Quick Reference Summary")
        print("  [Q] Quit")
        print("-"*70)
        
        choice = input("Your choice: ").strip().upper()
        
        if choice == '1':
            DemoSection1.run()
        elif choice == '2':
            DemoSection2.run()
        elif choice == '3':
            DemoSection3.run()
        elif choice == '4':
            InteractiveQuiz.run()
        elif choice == '5':
            print_quick_reference()
        elif choice == 'Q':
            print("\n👋 Thanks for learning about design patterns!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        if choice in ['1', '2', '3', '4', '5']:
            input("\n\nPress Enter to continue...")


def print_quick_reference():
    """Print a quick reference guide"""
    DemoSection.show_section("QUICK REFERENCE")
    
    print("""
FACTORY PATTERN
--------------
Purpose: Object Creation
Question: "What object should I create?"
When: At creation time
Result: Different objects

Example:
  factory.create("car") → Returns Car object
  factory.create("bike") → Returns Bike object

Use when:
  • You don't know which class to instantiate until runtime
  • You want to centralize object creation
  • Objects have different interfaces


STRATEGY PATTERN
---------------
Purpose: Behavior Selection  
Question: "How should this object behave?"
When: Can change at runtime
Result: Same object, different behavior

Example:
  navigator.set_strategy(CarStrategy())
  navigator.navigate() → Uses car routing
  
  navigator.set_strategy(WalkStrategy())
  navigator.navigate() → Uses walking routing

Use when:
  • You have multiple algorithms for the same task
  • You want to switch algorithms at runtime
  • You want to eliminate conditionals


MEMORY TRICK
-----------
Factory = Manufacturing Plant (creates products)
Strategy = Swiss Army Knife (same tool, different functions)

Factory: "I need a car" → 🏭 → New Car Object
Strategy: "Change driving mode" → 🚗 → Same car, different behavior
    """)


if __name__ == "__main__":
    main()