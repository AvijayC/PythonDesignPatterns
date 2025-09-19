# SQL Filter Validator

A Python tool for validating that SQL queries contain required filter conditions on specific table columns. This is particularly useful for ensuring data security and compliance rules are followed, such as always filtering out deleted records, test accounts, or reversed transactions.

## Purpose

When working with sensitive data, certain tables may require mandatory filtering conditions. For example:
- `users` table must always filter `deleted = 0`
- `accounts` table must always filter `is_test = 0`
- `transactions` table must always filter `reversed = 0`

This validator parses SQL queries and ensures these rules are followed, regardless of where in the query hierarchy the filter appears.

## Features

- **Comprehensive SQL Parsing**: Handles CTEs, subqueries, JOINs, and complex nested queries
- **Flexible Filter Location**: Detects filters in WHERE clauses, JOIN conditions, and across query levels
- **Alias Resolution**: Correctly tracks table aliases throughout the query
- **Detailed Violation Reporting**: Provides clear feedback on what's missing and where
- **Snowflake SQL Support**: Handles Snowflake-specific syntax like QUALIFY and FLATTEN

## Installation

```bash
pip install sqlglot
```

## Usage

### Basic Example

```python
from sql_filter_validator import SQLFilterValidator, SQLFilterRule

# Define validation rules
rules = [
    SQLFilterRule(table_name='users', column_name='deleted', required_value=0),
    SQLFilterRule(table_name='accounts', column_name='is_test', required_value=0),
]

# Create validator
validator = SQLFilterValidator(rules)

# Validate a query
sql = """
    SELECT *
    FROM users u
    JOIN accounts a ON a.id = u.account_id
    WHERE u.status = 'active'
      AND a.is_test = 0
"""

result = validator.validate(sql)

if not result.passed:
    for violation in result.violations:
        print(f"Missing filter: {violation.rule.table_name}.{violation.missing_filter}")
        print(f"Suggestion: {violation.suggestion}")
```

### Complex Query Example

The validator handles complex queries with CTEs and subqueries:

```python
sql = """
    WITH active_users AS (
        SELECT * FROM users WHERE deleted = 0
    ),
    valid_transactions AS (
        SELECT * FROM transactions WHERE reversed = 0
    )
    SELECT *
    FROM active_users au
    JOIN valid_transactions vt ON vt.user_id = au.id
"""

result = validator.validate(sql)
# This will pass as all required filters are present
```

## Filter Detection Scenarios

### 1. Same-Level Filters
Filter in the same query level as the table:
```sql
SELECT * FROM users WHERE deleted = 0
```

### 2. Upper-Level Filters
Filter applied to CTE or subquery columns in outer query:
```sql
WITH all_users AS (
    SELECT * FROM users
)
SELECT * FROM all_users WHERE deleted = 0
```

### 3. JOIN Condition Filters
Filter in JOIN ON clause:
```sql
SELECT *
FROM orders o
JOIN users u ON u.id = o.user_id AND u.deleted = 0
```

### 4. Nested Subquery Filters
Filter applied multiple levels up:
```sql
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM users
    ) t1
) t2 WHERE deleted = 0
```

## Classes

### SQLFilterRule
Defines a required filter condition:
```python
SQLFilterRule(
    table_name='users',
    column_name='deleted',
    required_value=0,
    operator=SQLFilterOperator.EQUALS
)
```

### SQLValidationResult
Contains validation results:
- `passed`: Boolean indicating if validation passed
- `violations`: List of rule violations
- `validated_tables`: Set of tables that were checked
- `table_usage`: Dict mapping tables to their usage locations
- `applied_filters`: Dict of detected filters by table.column

### SQLFilterValidator
Main validator class:
```python
validator = SQLFilterValidator(rules)
result = validator.validate(sql_query)
```

## Running Tests

```bash
# Run all tests
python -m pytest test_filter_validator.py -v

# Run specific test class
python -m pytest test_filter_validator.py::TestJoinFilters -v

# Run specific test
python -m pytest test_filter_validator.py::TestBasicFiltering::test_simple_where_filter_passes -v
```

## Test Coverage

The test suite includes:
- Basic WHERE clause filtering
- JOIN ON conditions vs WHERE conditions
- CTE (Common Table Expression) handling
- Subquery filters at various nesting levels
- Ambiguous column detection
- Complex multi-table scenarios
- Snowflake-specific SQL features
- Edge cases and error conditions

## Limitations

1. **SQL Parsing**: Uses `sqlglot` library which provides excellent support for multiple SQL dialects including Snowflake
2. **Ambiguous Columns**: When a column name exists in multiple tables without table prefix, the validator may not correctly identify which table is being filtered
3. **Dynamic SQL**: Cannot validate dynamically constructed SQL
4. **Complex Expressions**: May not detect filters within complex CASE statements or functions

## Design Patterns Used

- **Visitor Pattern**: Traverse SQL Abstract Syntax Tree
- **Chain of Responsibility**: Resolve filters through query hierarchy
- **Repository Pattern**: Store and retrieve filter rules
- **Data Transfer Object**: Result classes for clean API

## Future Enhancements

- Support for more SQL dialects
- Schema awareness for better ambiguous column handling
- Configuration file support for rules
- Integration with CI/CD pipelines
- Performance optimization for large queries
- Support for more complex filter conditions (LIKE, REGEX, etc.)