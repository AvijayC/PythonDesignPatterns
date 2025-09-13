#!/usr/bin/env python3
"""
Assertions vs Exceptions: When to Use Each
"""

import sys
from typing import List, Optional
from dataclasses import dataclass

# ==================================================================
# GOLDEN RULE: Assertions vs Exceptions
# ==================================================================
# - Assertions: For internal bugs that should NEVER happen (programmer errors)
# - Exceptions: For runtime errors that MIGHT happen (user input, network, etc.)
# 
# Assertions can be disabled with python -O (optimize mode)
# Never use assertions for:
#   - Input validation
#   - Permission checks  
#   - Handling runtime errors
# ==================================================================

# WRONG: Using assertions for input validation
def process_user_input_wrong(user_data: dict):
    """BAD: Assertions can be disabled in production!"""
    assert user_data is not None, "User data required"  # WRONG!
    assert 'email' in user_data, "Email required"  # WRONG!
    assert len(user_data['email']) > 0, "Email cannot be empty"  # WRONG!
    # In production with -O flag, these checks won't run!

# RIGHT: Using exceptions for input validation
def process_user_input_right(user_data: dict):
    """GOOD: Exceptions always run"""
    if user_data is None:
        raise ValueError("User data required")
    if 'email' not in user_data:
        raise KeyError("Email field required")
    if not user_data['email']:
        raise ValueError("Email cannot be empty")

# RIGHT: Using assertions for internal invariants
class BankAccount:
    """Example of proper assertion usage"""
    
    def __init__(self, initial_balance: float = 0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")  # User error
        
        self._balance = initial_balance
        # This should NEVER be false if our code is correct
        assert self._balance >= 0, "Internal error: negative balance"
    
    def deposit(self, amount: float):
        # Validate user input with exceptions
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        old_balance = self._balance
        self._balance += amount
        
        # Assert internal invariants (programmer errors)
        assert self._balance > old_balance, "Balance should increase after deposit"
        assert self._balance >= 0, "Balance should never be negative"
    
    def withdraw(self, amount: float):
        # User input validation
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError(f"Insufficient funds. Balance: {self._balance}")
        
        old_balance = self._balance
        self._balance -= amount
        
        # Internal consistency checks
        assert self._balance < old_balance, "Balance should decrease after withdrawal"
        assert self._balance >= 0, "Internal error: negative balance after withdrawal"
    
    @property
    def balance(self) -> float:
        # This invariant should always hold
        assert self._balance >= 0, "Internal state corruption"
        return self._balance

# Pattern 1: Pre and Post Conditions
def binary_search(sorted_list: List[int], target: int) -> int:
    """Binary search with assertions for algorithm correctness"""
    
    # Precondition: List must be sorted (programmer responsibility)
    # This is a bug if it fails - the caller violated the contract
    assert all(sorted_list[i] <= sorted_list[i+1] 
               for i in range(len(sorted_list)-1)), \
           "Precondition violated: list must be sorted"
    
    left, right = 0, len(sorted_list) - 1
    
    while left <= right:
        # Invariant: target must be in sorted_list[left:right+1] if it exists
        assert 0 <= left <= right < len(sorted_list), \
               "Search bounds corrupted"
        
        mid = (left + right) // 2
        
        if sorted_list[mid] == target:
            # Postcondition: We found the target
            assert sorted_list[mid] == target, "Found index doesn't match target"
            return mid
        elif sorted_list[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    # Postcondition: Target not in list
    assert target not in sorted_list, "Failed to find existing target"
    return -1

# Pattern 2: State Machine Validation
class OrderStateMachine:
    """Order processing with state validation"""
    
    STATES = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
    TRANSITIONS = {
        'pending': ['paid', 'cancelled'],
        'paid': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': [],
        'cancelled': []
    }
    
    def __init__(self):
        self._state = 'pending'
    
    def transition_to(self, new_state: str):
        """Transition to new state with validation"""
        
        # User input validation (might be invalid)
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state: {new_state}")
        
        if new_state not in self.TRANSITIONS[self._state]:
            raise ValueError(
                f"Invalid transition from {self._state} to {new_state}"
            )
        
        old_state = self._state
        self._state = new_state
        
        # Internal consistency (should never fail if code is correct)
        assert self._state in self.STATES, "Corrupted state after transition"
        assert old_state != self._state, "State should have changed"

# Pattern 3: Debug Assertions (Only in Development)
def complex_algorithm(data: List[float]) -> float:
    """Algorithm with debug assertions"""
    
    if not data:
        raise ValueError("Cannot process empty data")
    
    # Expensive check only in debug mode
    if __debug__:  # This block is removed with -O flag
        print("Debug mode: Running expensive validation")
        # Expensive validation that would slow production
        assert all(isinstance(x, (int, float)) for x in data), \
               "All elements must be numeric"
        assert len(set(data)) == len(data), \
               "Debug check: Duplicate values detected"
    
    result = sum(data) / len(data)
    
    # Sanity check that should never fail
    assert isinstance(result, (int, float)), "Result type corrupted"
    
    return result

# Pattern 4: Contract Programming
class DataProcessor:
    """Design by contract pattern"""
    
    def __init__(self, batch_size: int):
        # Validate constructor input
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        self.batch_size = batch_size
        self._processed_count = 0
        
        # Class invariant
        self._check_invariants()
    
    def _check_invariants(self):
        """Class invariants that should always hold"""
        assert self.batch_size > 0, "Batch size corrupted"
        assert self._processed_count >= 0, "Negative processed count"
        assert isinstance(self._processed_count, int), "Count type corrupted"
    
    def process_batch(self, items: List):
        """Process items with contract validation"""
        
        # Preconditions (user's responsibility)
        if not items:
            raise ValueError("Cannot process empty batch")
        if len(items) > self.batch_size:
            raise ValueError(f"Batch too large: {len(items)} > {self.batch_size}")
        
        # Remember old state for postcondition check
        old_count = self._processed_count
        
        # Process items (simplified)
        for item in items:
            # Process item...
            self._processed_count += 1
        
        # Postconditions (our responsibility)
        assert self._processed_count == old_count + len(items), \
               "Processed count mismatch"
        
        # Check invariants still hold
        self._check_invariants()
        
        return self._processed_count

# Pattern 5: Fail-Fast with Guard Clauses
def calculate_discount(price: float, discount_percent: float, 
                       is_premium: bool = False) -> float:
    """Calculate discount with guard clauses"""
    
    # Guard clauses - fail fast on invalid input
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    
    # Business logic
    max_discount = 50 if not is_premium else 75
    actual_discount = min(discount_percent, max_discount)
    
    discounted_price = price * (1 - actual_discount / 100)
    
    # Sanity checks (should never fail)
    assert 0 <= discounted_price <= price, \
           f"Discounted price {discounted_price} out of range"
    assert actual_discount <= max_discount, \
           "Discount exceeded maximum"
    
    return discounted_price

# Pattern 6: Custom Assertion Functions
def assert_valid_percentage(value: float, name: str = "value"):
    """Custom assertion for common checks"""
    assert isinstance(value, (int, float)), \
           f"{name} must be numeric, got {type(value)}"
    assert 0 <= value <= 100, \
           f"{name} must be between 0 and 100, got {value}"

def assert_non_empty_string(value: str, name: str = "value"):
    """Assert string is non-empty"""
    assert isinstance(value, str), \
           f"{name} must be string, got {type(value)}"
    assert value.strip(), \
           f"{name} cannot be empty or whitespace"

# Pattern 7: Testing vs Production Assertions
class CriticalSystem:
    """System with different assertion levels"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self._state = "initialized"
    
    def critical_operation(self, value: float):
        """Operation with layered validation"""
        
        # Always validate user input
        if value <= 0:
            raise ValueError("Value must be positive")
        
        # Debug-only expensive checks
        if self.debug_mode:
            assert self._validate_system_state(), \
                   "System state validation failed"
            print(f"Debug: Processing value {value}")
        
        # Critical assertions that should always run
        # (But remember: can still be disabled with -O)
        assert self._state != "error", "System in error state"
        
        # Process...
        result = value * 2
        
        # Postcondition
        assert result > value, "Result should be greater than input"
        
        return result
    
    def _validate_system_state(self) -> bool:
        """Expensive validation for debug mode"""
        # Simulate expensive check
        import time
        time.sleep(0.01)
        return True

# Best Practices Summary
def demonstrate_best_practices():
    """Show when to use assertions vs exceptions"""
    
    print("Best Practices for Assertions vs Exceptions\n")
    print("="*50)
    
    # 1. Input validation - use exceptions
    print("\n1. Input Validation - USE EXCEPTIONS:")
    try:
        process_user_input_right(None)
    except ValueError as e:
        print(f"   Correctly caught: {e}")
    
    # 2. Internal invariants - use assertions
    print("\n2. Internal Invariants - USE ASSERTIONS:")
    account = BankAccount(100)
    account.deposit(50)
    print(f"   Balance: {account.balance} (assertions ensure >= 0)")
    
    # 3. Algorithm preconditions - use assertions
    print("\n3. Algorithm Preconditions - USE ASSERTIONS:")
    sorted_data = [1, 3, 5, 7, 9]
    index = binary_search(sorted_data, 5)
    print(f"   Found 5 at index: {index}")
    
    # 4. State validation - mixed approach
    print("\n4. State Validation - MIXED APPROACH:")
    order = OrderStateMachine()
    try:
        order.transition_to('paid')
        print("   Valid transition: pending -> paid")
        order.transition_to('delivered')  # Invalid
    except ValueError as e:
        print(f"   Invalid transition caught: {e}")
    
    # 5. Debug vs production
    print("\n5. Debug Mode Checks:")
    print(f"   Debug mode active: {__debug__}")
    result = complex_algorithm([1, 2, 3, 4, 5])
    print(f"   Result: {result}")
    
    # 6. Guard clauses
    print("\n6. Guard Clauses - FAIL FAST:")
    try:
        price = calculate_discount(100, 30, is_premium=True)
        print(f"   Discounted price: ${price:.2f}")
        price = calculate_discount(-50, 20)  # Invalid
    except ValueError as e:
        print(f"   Invalid input caught: {e}")

if __name__ == "__main__":
    demonstrate_best_practices()
    
    print("\n" + "="*50)
    print("Remember:")
    print("- Assertions: For bugs that should NEVER happen")
    print("- Exceptions: For errors that MIGHT happen")
    print("- Assertions can be disabled with 'python -O'")
    print("- Never use assertions for security or input validation!")