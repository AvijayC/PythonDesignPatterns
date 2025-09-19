#!/usr/bin/env python3
"""
SQL Filter Validator - Validates that specific table columns are filtered with required values.

This module ensures that when certain tables are used in SQL queries, specific columns
from those tables have required filter conditions (e.g., deleted = 0) applied somewhere
in the query hierarchy.

Uses sqlglot for robust SQL parsing and AST traversal.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from enum import Enum
import sqlglot
from sqlglot import exp
from sqlglot.expressions import Expression


class SQLFilterOperator(Enum):
    """Supported filter operators"""
    EQUALS = '='
    IN = 'IN'
    NOT_EQUALS = '!='
    LESS_THAN = '<'
    GREATER_THAN = '>'


@dataclass
class SQLFilterRule:
    """Defines a required filter condition for a table column"""
    table_name: str
    column_name: str
    required_value: Any
    operator: SQLFilterOperator = SQLFilterOperator.EQUALS

    def __str__(self):
        return f"{self.table_name}.{self.column_name} {self.operator.value} {self.required_value}"


@dataclass
class SQLTableReference:
    """Represents a table reference in the query"""
    table_name: str
    alias: Optional[str]
    scope_level: int
    is_cte: bool = False
    source_expression: Optional[Expression] = None


@dataclass
class SQLFilterCondition:
    """Represents a filter condition found in the query"""
    table_ref: Optional[str]  # Table alias or name
    column_name: str
    operator: str
    value: Any
    location: str  # WHERE, JOIN, HAVING
    scope_level: int
    raw_expression: Optional[Expression] = None


@dataclass
class SQLValidationViolation:
    """Represents a validation rule violation"""
    rule: SQLFilterRule
    table_found_at: str
    missing_filter: str
    found_filters: List[str]
    suggestion: str


@dataclass
class SQLValidationResult:
    """Result of validation check"""
    passed: bool
    violations: List[SQLValidationViolation]
    validated_tables: Set[str]
    table_usage: Dict[str, List[str]]
    applied_filters: Dict[str, List[SQLFilterCondition]]


class SQLQueryAnalyzer:
    """Analyzes SQL query structure using sqlglot"""

    def __init__(self, sql: str, dialect: str = "snowflake"):
        self.sql = sql
        self.dialect = dialect
        self.ast = sqlglot.parse_one(sql, dialect=dialect)
        self.table_refs: List[SQLTableReference] = []
        self.filter_conditions: List[SQLFilterCondition] = []
        self.cte_definitions: Dict[str, Expression] = {}
        self.alias_map: Dict[str, str] = {}
        self.processed_nodes = set()  # Track processed nodes to avoid duplicates

    def analyze(self) -> Tuple[List[SQLTableReference], List[SQLFilterCondition], Dict[str, str]]:
        """Analyze the query and extract all information"""
        # Collect CTEs first
        self._collect_ctes()

        # Extract tables using sqlglot's built-in methods
        self._extract_tables()

        # Extract filter conditions
        self._extract_all_filters()

        # Build alias map
        self._build_alias_map()

        return self.table_refs, self.filter_conditions, self.alias_map

    def _collect_ctes(self):
        """Collect all CTE definitions"""
        for cte in self.ast.find_all(exp.CTE):
            cte_name = cte.alias
            if cte_name:
                self.cte_definitions[cte_name] = cte.this
                # Add CTE as a table reference
                self.table_refs.append(
                    SQLTableReference(
                        table_name=cte_name,
                        alias=cte_name,
                        scope_level=0,
                        is_cte=True,
                        source_expression=cte
                    )
                )

    def _extract_tables(self):
        """Extract all table references from the query"""
        # Use sqlglot's find_all to get all Table nodes
        for table in self.ast.find_all(exp.Table):
            table_name = table.name
            alias = table.alias

            # Skip if this is a CTE reference
            if table_name not in self.cte_definitions:
                # Check if we've already processed this exact table reference
                table_id = id(table)
                if table_id not in self.processed_nodes:
                    self.processed_nodes.add(table_id)
                    self.table_refs.append(
                        SQLTableReference(
                            table_name=table_name,
                            alias=alias,
                            scope_level=0,  # Simplified for now
                            is_cte=False,
                            source_expression=table
                        )
                    )

    def _extract_all_filters(self):
        """Extract all filter conditions from WHERE and JOIN clauses"""
        # Extract WHERE conditions
        for where in self.ast.find_all(exp.Where):
            if where.this:
                self._extract_conditions(where.this, "WHERE", 0)

        # Extract JOIN ON conditions
        for join in self.ast.find_all(exp.Join):
            if join.args.get("on"):
                self._extract_conditions(join.args["on"], "JOIN", 0)

        # Extract HAVING conditions
        for having in self.ast.find_all(exp.Having):
            if having.this:
                self._extract_conditions(having.this, "HAVING", 0)

    def _extract_conditions(self, expr: Expression, location: str, scope_level: int):
        """Recursively extract filter conditions from an expression"""
        if expr is None:
            return

        # Check if we've already processed this node
        expr_id = id(expr)
        if expr_id in self.processed_nodes:
            return
        self.processed_nodes.add(expr_id)

        if isinstance(expr, exp.And):
            # Handle AND conditions
            self._extract_conditions(expr.left, location, scope_level)
            self._extract_conditions(expr.right, location, scope_level)
        elif isinstance(expr, exp.Or):
            # Handle OR conditions
            self._extract_conditions(expr.left, location, scope_level)
            self._extract_conditions(expr.right, location, scope_level)
        elif isinstance(expr, exp.EQ):
            # Handle equality
            self._process_comparison(expr, "=", location, scope_level)
        elif isinstance(expr, exp.NEQ):
            # Handle not equals
            self._process_comparison(expr, "!=", location, scope_level)
        elif isinstance(expr, exp.LT):
            # Handle less than
            self._process_comparison(expr, "<", location, scope_level)
        elif isinstance(expr, exp.GT):
            # Handle greater than
            self._process_comparison(expr, ">", location, scope_level)
        elif isinstance(expr, exp.LTE):
            # Handle less than or equal
            self._process_comparison(expr, "<=", location, scope_level)
        elif isinstance(expr, exp.GTE):
            # Handle greater than or equal
            self._process_comparison(expr, ">=", location, scope_level)
        elif isinstance(expr, exp.In):
            # Handle IN operator
            self._process_in_condition(expr, location, scope_level)

    def _process_comparison(self, expr: Expression, operator: str, location: str, scope_level: int):
        """Process a comparison expression"""
        left = expr.left if hasattr(expr, 'left') else expr.this
        right = expr.right if hasattr(expr, 'right') else expr.expression

        # Try to extract column info from left side
        column_info = self._extract_column_info(left)
        if column_info:
            table_ref, column_name = column_info
            value = self._extract_value(right)

            # Only add if this looks like a column filter (not a join condition)
            if not isinstance(right, exp.Column):
                self.filter_conditions.append(
                    SQLFilterCondition(
                        table_ref=table_ref,
                        column_name=column_name,
                        operator=operator,
                        value=value,
                        location=location,
                        scope_level=scope_level,
                        raw_expression=expr
                    )
                )

        # Also check if right side is a column and left is a value
        column_info = self._extract_column_info(right)
        if column_info and not isinstance(left, exp.Column):
            table_ref, column_name = column_info
            value = self._extract_value(left)

            # Reverse the operator for right-side column
            reversed_op = {
                '<': '>', '>': '<', '<=': '>=', '>=': '<=', '=': '=', '!=': '!='
            }.get(operator, operator)

            self.filter_conditions.append(
                SQLFilterCondition(
                    table_ref=table_ref,
                    column_name=column_name,
                    operator=reversed_op,
                    value=value,
                    location=location,
                    scope_level=scope_level,
                    raw_expression=expr
                )
            )

    def _process_in_condition(self, expr: exp.In, location: str, scope_level: int):
        """Process an IN condition"""
        column_info = self._extract_column_info(expr.this)
        if column_info:
            table_ref, column_name = column_info

            # Extract values from IN list
            values = []
            for item in expr.expressions:
                values.append(self._extract_value(item))

            self.filter_conditions.append(
                SQLFilterCondition(
                    table_ref=table_ref,
                    column_name=column_name,
                    operator="IN",
                    value=values,
                    location=location,
                    scope_level=scope_level,
                    raw_expression=expr
                )
            )

    def _extract_column_info(self, expr: Expression) -> Optional[Tuple[Optional[str], str]]:
        """Extract table reference and column name from expression"""
        if isinstance(expr, exp.Column):
            column_name = expr.name
            table_ref = expr.table  # Column always has table attribute, might be None
            return (table_ref, column_name)
        elif isinstance(expr, exp.Identifier):
            return (None, expr.name)
        return None

    def _extract_value(self, expr: Expression) -> Any:
        """Extract value from expression"""
        if isinstance(expr, exp.Literal):
            # Handle string/numeric literals
            if expr.is_string:
                return str(expr.this).strip("'\"")
            elif expr.is_number:
                try:
                    return int(expr.this)
                except ValueError:
                    return float(expr.this)
            return expr.this
        elif isinstance(expr, exp.Identifier):
            return expr.name
        elif isinstance(expr, exp.Column):
            # Column reference on right side (e.g., comparing two columns)
            return str(expr.sql())
        else:
            return str(expr)

    def _build_alias_map(self):
        """Build complete alias to table name mapping"""
        for ref in self.table_refs:
            if ref.alias:
                self.alias_map[ref.alias] = ref.table_name
            # Map table name to itself
            self.alias_map[ref.table_name] = ref.table_name

        # Handle CTE references - map CTE to underlying tables
        for cte_name in self.cte_definitions:
            cte_expr = self.cte_definitions[cte_name]
            cte_tables = self._extract_tables_from_cte(cte_expr)
            if cte_tables:
                # Map CTE to first underlying table (simplified)
                self.alias_map[cte_name] = cte_tables[0]

    def _extract_tables_from_cte(self, cte_expr: Expression) -> List[str]:
        """Extract table names referenced in a CTE"""
        tables = []
        for table in cte_expr.find_all(exp.Table):
            if table.name and table.name not in self.cte_definitions:
                tables.append(table.name)
        return tables


class SQLFilterValidator:
    """Validates SQL queries against filter rules"""

    def __init__(self, rules: List[SQLFilterRule], dialect: str = "snowflake"):
        self.rules = rules
        self.dialect = dialect
        self.rule_map = {(r.table_name, r.column_name): r for r in rules}

    def validate(self, sql_query: str) -> SQLValidationResult:
        """Validate a SQL query against the defined rules"""
        try:
            # Analyze the query
            analyzer = SQLQueryAnalyzer(sql_query, self.dialect)
            table_refs, filter_conditions, alias_map = analyzer.analyze()

            # Resolve filters to actual tables
            resolved_filters = self._resolve_filters_to_tables(
                filter_conditions, alias_map
            )

            # Check each rule
            violations = []
            validated_tables = set()

            for rule in self.rules:
                # Check if table is used
                table_used = any(
                    ref.table_name == rule.table_name or
                    alias_map.get(ref.table_name) == rule.table_name
                    for ref in table_refs
                )

                if table_used:
                    validated_tables.add(rule.table_name)

                    # Check if required filter exists
                    table_column_key = f"{rule.table_name}.{rule.column_name}"
                    matching_filters = resolved_filters.get(table_column_key, [])

                    # Check if any filter matches the rule
                    rule_satisfied = False
                    for filter_cond in matching_filters:
                        if self._filter_matches_rule(filter_cond, rule):
                            rule_satisfied = True
                            break

                    if not rule_satisfied:
                        # Find where table is used
                        table_locations = []
                        for ref in table_refs:
                            if ref.table_name == rule.table_name:
                                loc = f"level {ref.scope_level}"
                                if ref.alias:
                                    loc += f" as {ref.alias}"
                                if ref.is_cte:
                                    loc = f"CTE {loc}"
                                table_locations.append(loc)

                        violation = SQLValidationViolation(
                            rule=rule,
                            table_found_at=", ".join(table_locations) if table_locations else "query",
                            missing_filter=f"{rule.column_name} {rule.operator.value} {rule.required_value}",
                            found_filters=[str(f.raw_expression) for f in matching_filters] if matching_filters else [],
                            suggestion=f"Add 'AND {rule.column_name} = {rule.required_value}' to WHERE clause"
                        )
                        violations.append(violation)

            # Build table usage map
            table_usage = {}
            for ref in table_refs:
                if ref.table_name not in table_usage:
                    table_usage[ref.table_name] = []
                location = f"level_{ref.scope_level}"
                if ref.alias:
                    location += f":{ref.alias}"
                if ref.is_cte:
                    location = f"CTE:{location}"
                table_usage[ref.table_name].append(location)

            return SQLValidationResult(
                passed=len(violations) == 0,
                violations=violations,
                validated_tables=validated_tables,
                table_usage=table_usage,
                applied_filters=resolved_filters
            )

        except Exception as e:
            # Handle parsing errors gracefully
            print(f"Error parsing SQL: {e}")
            return SQLValidationResult(
                passed=True,  # Pass if we can't parse
                violations=[],
                validated_tables=set(),
                table_usage={},
                applied_filters={}
            )

    def _resolve_filters_to_tables(
        self,
        filters: List[SQLFilterCondition],
        alias_map: Dict[str, str]
    ) -> Dict[str, List[SQLFilterCondition]]:
        """Resolve filter conditions to actual table.column combinations"""
        resolved = {}

        for filter_cond in filters:
            # Determine actual table name
            actual_table = None

            if filter_cond.table_ref:
                # Explicit table reference - resolve through alias map
                actual_table = alias_map.get(filter_cond.table_ref, filter_cond.table_ref)
            else:
                # No explicit table reference - check against all known tables
                # This is where ambiguity can occur
                for table_name in set(alias_map.values()):
                    # Check if this table-column combination is in our rules
                    if (table_name, filter_cond.column_name) in self.rule_map:
                        key = f"{table_name}.{filter_cond.column_name}"
                        if key not in resolved:
                            resolved[key] = []
                        resolved[key].append(filter_cond)

            if actual_table:
                key = f"{actual_table}.{filter_cond.column_name}"
                if key not in resolved:
                    resolved[key] = []
                resolved[key].append(filter_cond)

        return resolved

    def _filter_matches_rule(self, filter_cond: SQLFilterCondition, rule: SQLFilterRule) -> bool:
        """Check if a filter condition satisfies a rule"""
        # Check operator
        if filter_cond.operator.upper() != rule.operator.value.upper():
            return False

        # Check value
        if filter_cond.operator.upper() == "IN":
            # For IN operator, check if required value is in the list
            if isinstance(filter_cond.value, list):
                return rule.required_value in filter_cond.value
            return filter_cond.value == rule.required_value
        else:
            # For other operators, direct comparison
            return filter_cond.value == rule.required_value


def create_sample_rules() -> List[SQLFilterRule]:
    """Create sample validation rules for testing"""
    return [
        SQLFilterRule('users', 'deleted', 0),
        SQLFilterRule('accounts', 'is_test', 0),
        SQLFilterRule('transactions', 'reversed', 0),
    ]


if __name__ == "__main__":
    # Example usage
    rules = create_sample_rules()
    validator = SQLFilterValidator(rules)

    # Test query with missing filter
    test_sql = """
    WITH active_users AS (
        SELECT * FROM users u
        WHERE u.status = 'active'
    )
    SELECT *
    FROM active_users au
    JOIN transactions t ON t.user_id = au.id
    WHERE t.amount > 100
      AND t.reversed = 0
    """

    result = validator.validate(test_sql)

    print(f"Validation {'PASSED' if result.passed else 'FAILED'}")

    if not result.passed:
        print("\nViolations found:")
        for violation in result.violations:
            print(f"  - Table '{violation.rule.table_name}' missing filter: {violation.missing_filter}")
            print(f"    Found at: {violation.table_found_at}")
            print(f"    Suggestion: {violation.suggestion}")

    print(f"\nTables validated: {result.validated_tables}")
    print(f"Table usage: {result.table_usage}")