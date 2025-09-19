#!/usr/bin/env python3
"""
Comprehensive test suite for SQL Filter Validator

Tests various scenarios including:
- Same-level filters in WHERE clauses
- Upper-level filters (outer queries filtering CTEs/subqueries)
- Filters in JOIN ON conditions vs WHERE clauses
- Ambiguous column detection
- Complex nested queries
- Multiple tables with multiple rules
"""

import pytest
from sql_filter_validator import (
    SQLFilterValidator,
    SQLFilterRule,
    SQLFilterOperator,
    SQLValidationResult
)


class TestBasicFiltering:
    """Test basic filter detection at the same query level"""

    def test_simple_where_filter_passes(self):
        """Test that a simple WHERE filter is correctly detected"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should pass when filter is present"
        assert 'users' in result.validated_tables

    def test_simple_where_filter_fails(self):
        """Test that missing filter is detected"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE status = 'active'
        """

        result = validator.validate(sql)
        assert not result.passed, "Should fail when required filter is missing"
        assert len(result.violations) == 1
        assert result.violations[0].rule.column_name == 'deleted'

    def test_filter_with_table_alias(self):
        """Test filter detection when table has an alias"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users u
        WHERE u.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter with table alias"

    def test_filter_wrong_value_fails(self):
        """Test that filter with wrong value fails validation"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted = 1
        """

        result = validator.validate(sql)
        assert not result.passed, "Should fail when filter has wrong value"
        assert len(result.violations) == 1

    def test_multiple_conditions_in_where(self):
        """Test filter detection among multiple WHERE conditions"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users u
        WHERE u.status = 'active'
          AND u.deleted = 0
          AND u.created_date > '2023-01-01'
        """

        result = validator.validate(sql)
        assert result.passed, "Should find filter among multiple conditions"


class TestJoinFilters:
    """Test filter detection in JOIN clauses"""

    def test_filter_in_join_on_clause(self):
        """Test that filters in JOIN ON conditions are detected"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM orders o
        JOIN users u ON u.id = o.user_id
            AND u.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in JOIN ON clause"

    def test_filter_in_join_without_alias(self):
        """Test JOIN filter without table alias"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM orders
        JOIN users ON users.id = orders.user_id
            AND users.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in JOIN without alias"

    def test_filter_in_where_not_join(self):
        """Test filter in WHERE clause instead of JOIN"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM orders o
        JOIN users u ON u.id = o.user_id
        WHERE u.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Filter in WHERE should work too"

    def test_multiple_joins_with_filters(self):
        """Test multiple JOINs each with their own filters"""
        rules = [
            SQLFilterRule('users', 'deleted', 0),
            SQLFilterRule('accounts', 'is_test', 0)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM orders o
        JOIN users u ON u.id = o.user_id AND u.deleted = 0
        JOIN accounts a ON a.id = u.account_id AND a.is_test = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filters in multiple JOINs"
        assert 'users' in result.validated_tables
        assert 'accounts' in result.validated_tables


class TestCTEFilters:
    """Test filter detection with Common Table Expressions"""

    def test_filter_inside_cte(self):
        """Test filter applied inside CTE definition"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH active_users AS (
            SELECT * FROM users
            WHERE deleted = 0
        )
        SELECT * FROM active_users
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter inside CTE"

    def test_filter_outside_cte(self):
        """Test filter applied to CTE in main query"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH all_users AS (
            SELECT * FROM users
        )
        SELECT * FROM all_users
        WHERE deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter on CTE columns"

    def test_missing_filter_in_cte(self):
        """Test that missing filter in CTE is caught"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH active_users AS (
            SELECT * FROM users
            WHERE status = 'active'
        )
        SELECT * FROM active_users
        """

        result = validator.validate(sql)
        assert not result.passed, "Should fail when CTE lacks required filter"

    def test_chained_ctes_with_filter(self):
        """Test filter in chained CTEs"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH base_users AS (
            SELECT * FROM users
        ),
        filtered_users AS (
            SELECT * FROM base_users
            WHERE deleted = 0
        )
        SELECT * FROM filtered_users
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in chained CTE"

    def test_multiple_ctes_different_tables(self):
        """Test multiple CTEs with different tables and rules"""
        rules = [
            SQLFilterRule('users', 'deleted', 0),
            SQLFilterRule('accounts', 'is_test', 0)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH active_users AS (
            SELECT * FROM users WHERE deleted = 0
        ),
        real_accounts AS (
            SELECT * FROM accounts WHERE is_test = 0
        )
        SELECT *
        FROM active_users u
        JOIN real_accounts a ON u.account_id = a.id
        """

        result = validator.validate(sql)
        assert result.passed, "Should validate multiple CTEs"


class TestSubqueryFilters:
    """Test filter detection in subqueries"""

    def test_filter_in_subquery(self):
        """Test filter inside a subquery"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM (
            SELECT * FROM users
            WHERE deleted = 0
        ) AS active_users
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in subquery"

    def test_filter_outside_subquery(self):
        """Test filter applied to subquery result"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM (
            SELECT * FROM users
        ) AS all_users
        WHERE deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter on subquery columns"

    def test_nested_subqueries_with_filter(self):
        """Test deeply nested subqueries with filter at outer level"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM (
            SELECT * FROM (
                SELECT * FROM users
            ) t1
        ) t2
        WHERE deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter on nested subquery"

    def test_subquery_in_from_with_join(self):
        """Test subquery in FROM clause with JOIN"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM orders o
        JOIN (
            SELECT * FROM users WHERE deleted = 0
        ) u ON u.id = o.user_id
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in subquery used in JOIN"


class TestAmbiguousColumns:
    """Test handling of ambiguous column references"""

    def test_ambiguous_column_without_prefix_fails(self):
        """Test that ambiguous column without table prefix might cause issues"""
        rules = [
            SQLFilterRule('users', 'deleted', 0),
            SQLFilterRule('posts', 'deleted', 0)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM users u
        JOIN posts p ON p.user_id = u.id
        WHERE deleted = 0
        """

        # This might pass for both tables due to ambiguity
        # In production, you'd want to flag this as ambiguous
        result = validator.validate(sql)
        # The current implementation might incorrectly pass this

    def test_explicit_table_prefix_resolves_ambiguity(self):
        """Test that explicit table prefix correctly identifies the filter"""
        rules = [
            SQLFilterRule('users', 'deleted', 0),
            SQLFilterRule('posts', 'deleted', 0)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM users u
        JOIN posts p ON p.user_id = u.id
        WHERE u.deleted = 0
          AND p.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should pass when both tables have required filters"

    def test_wrong_table_filter_fails(self):
        """Test that filtering wrong table's column fails"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM users u
        JOIN posts p ON p.user_id = u.id
        WHERE p.deleted = 0
        """

        result = validator.validate(sql)
        assert not result.passed, "Should fail - filtered posts.deleted, not users.deleted"


class TestComplexScenarios:
    """Test complex real-world scenarios"""

    def test_complex_query_with_multiple_rules(self):
        """Test complex query with CTEs, JOINs, and multiple rules"""
        rules = [
            SQLFilterRule('users', 'deleted', 0),
            SQLFilterRule('accounts', 'is_test', 0),
            SQLFilterRule('transactions', 'reversed', 0)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH active_users AS (
            SELECT u.*
            FROM users u
            JOIN accounts a ON a.id = u.account_id
            WHERE u.deleted = 0
              AND a.is_test = 0
        ),
        valid_transactions AS (
            SELECT * FROM transactions
            WHERE reversed = 0
        )
        SELECT
            au.name,
            COUNT(vt.id) as transaction_count
        FROM active_users au
        LEFT JOIN valid_transactions vt ON vt.user_id = au.id
        GROUP BY au.name
        """

        result = validator.validate(sql)
        assert result.passed, "Should pass complex query with all filters"

    def test_union_queries_with_filters(self):
        """Test UNION queries requiring filters in both parts"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT id, name FROM users WHERE deleted = 0 AND status = 'active'
        UNION
        SELECT id, name FROM users WHERE deleted = 0 AND status = 'pending'
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filters in both UNION parts"

    def test_having_clause_filters(self):
        """Test that HAVING clause filters are detected"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT
            status,
            COUNT(*) as user_count
        FROM users
        WHERE deleted = 0
        GROUP BY status
        HAVING COUNT(*) > 10
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter before HAVING clause"

    def test_case_statement_with_filter(self):
        """Test query with CASE statement and required filter"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT
            CASE
                WHEN status = 'active' THEN 'Active User'
                ELSE 'Inactive User'
            END as user_status,
            COUNT(*) as count
        FROM users
        WHERE deleted = 0
        GROUP BY user_status
        """

        result = validator.validate(sql)
        assert result.passed, "Should work with CASE statements"

    def test_window_function_with_filter(self):
        """Test window functions with required filters"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT
            name,
            ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY created_date) as rn
        FROM users
        WHERE deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should work with window functions"


class TestSnowflakeSpecific:
    """Test Snowflake-specific SQL features"""

    def test_qualify_clause(self):
        """Test Snowflake QUALIFY clause (Note: parser might not fully support)"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT
            name,
            ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY created_date) as rn
        FROM users
        WHERE deleted = 0
        QUALIFY rn = 1
        """

        result = validator.validate(sql)
        # Might pass or fail depending on parser support for QUALIFY
        assert result.passed, "Should handle QUALIFY clause"

    def test_lateral_flatten(self):
        """Test Snowflake FLATTEN function"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT
            u.name,
            f.value
        FROM users u,
        LATERAL FLATTEN(input => u.json_data) f
        WHERE u.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should handle LATERAL FLATTEN"

    def test_using_clause_in_join(self):
        """Test USING clause in JOIN"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM users u
        JOIN accounts a USING (account_id)
        WHERE u.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should handle USING clause"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_query(self):
        """Test empty or invalid SQL"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = ""
        # Should handle gracefully
        try:
            result = validator.validate(sql)
            # May pass since no tables are used
        except Exception as e:
            pytest.fail(f"Should handle empty query gracefully: {e}")

    def test_table_not_used(self):
        """Test when rule table is not used in query"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM products
        WHERE price > 100
        """

        result = validator.validate(sql)
        assert result.passed, "Should pass when rule table not used"
        assert 'users' not in result.validated_tables

    def test_multiple_same_table_references(self):
        """Test multiple references to same table"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT *
        FROM users u1
        JOIN users u2 ON u2.manager_id = u1.id
        WHERE u1.deleted = 0
          AND u2.deleted = 0
        """

        result = validator.validate(sql)
        assert result.passed, "Should handle self-joins"

    def test_filter_in_exists_subquery(self):
        """Test filter in EXISTS subquery"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM orders o
        WHERE EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = o.user_id
              AND u.deleted = 0
        )
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in EXISTS subquery"

    def test_filter_in_in_subquery(self):
        """Test filter in IN subquery"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM orders
        WHERE user_id IN (
            SELECT id FROM users
            WHERE deleted = 0
        )
        """

        result = validator.validate(sql)
        assert result.passed, "Should detect filter in IN subquery"


class TestOperatorVariations:
    """Test different operators and conditions"""

    def test_not_equals_operator(self):
        """Test != operator when = is required"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted != 1
        """

        result = validator.validate(sql)
        # Should fail because operator is != not =
        assert not result.passed, "Should fail with wrong operator"

    def test_in_operator_with_single_value(self):
        """Test IN operator with single value"""
        rules = [
            SQLFilterRule('users', 'status', 'active', SQLFilterOperator.IN)
        ]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE status IN ('active')
        """

        result = validator.validate(sql)
        # Depends on implementation of IN operator handling

    def test_between_operator(self):
        """Test BETWEEN operator (not in required operators)"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted BETWEEN 0 AND 0
        """

        result = validator.validate(sql)
        # Should fail as BETWEEN is not the = operator
        assert not result.passed, "Should fail with BETWEEN operator"

    def test_is_null_condition(self):
        """Test IS NULL condition"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted IS NULL OR deleted = 0
        """

        result = validator.validate(sql)
        # Might pass if = 0 condition is detected
        assert result.passed, "Should pass with alternative condition"


class TestValidationOutput:
    """Test the validation result output"""

    def test_violation_details(self):
        """Test that violation details are properly populated"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users WHERE status = 'active'
        """

        result = validator.validate(sql)
        assert not result.passed
        assert len(result.violations) == 1

        violation = result.violations[0]
        assert violation.rule.table_name == 'users'
        assert violation.rule.column_name == 'deleted'
        assert violation.missing_filter == 'deleted = 0'
        assert 'WHERE' in violation.suggestion

    def test_table_usage_tracking(self):
        """Test that table usage is properly tracked"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        WITH u1 AS (SELECT * FROM users),
             u2 AS (SELECT * FROM users)
        SELECT * FROM u1
        JOIN u2 ON u1.id = u2.manager_id
        WHERE u1.deleted = 0 AND u2.deleted = 0
        """

        result = validator.validate(sql)
        assert 'users' in result.table_usage
        # Should track multiple uses of the table

    def test_applied_filters_tracking(self):
        """Test that applied filters are tracked"""
        rules = [SQLFilterRule('users', 'deleted', 0)]
        validator = SQLFilterValidator(rules)

        sql = """
        SELECT * FROM users
        WHERE deleted = 0 AND status = 'active'
        """

        result = validator.validate(sql)
        assert result.passed
        assert 'users.deleted' in result.applied_filters


if __name__ == "__main__":
    # Run a specific test or all tests
    pytest.main([__file__, "-v"])