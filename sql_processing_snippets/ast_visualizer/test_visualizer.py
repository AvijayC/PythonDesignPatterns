"""
Test script for SQL AST Visualizer
Demonstrates all features including composable graphs, validation, and pipelines
"""

import os
from sql_ast_visualizer import SQLASTVisualizer, SnowflakeSchema
from test_schemas import get_all_schemas, create_mock_spark_df
from sql_query_examples import QUERY_EXAMPLES, ETL_PIPELINE


def test_single_query_visualization():
    """Test basic single query visualization"""
    print("\n" + "="*60)
    print("TEST 1: Single Query Visualization")
    print("="*60)

    # Create visualizer with schemas
    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    # Visualize a simple query
    query = QUERY_EXAMPLES["simple_join"]
    print(f"Visualizing simple join query...")
    print(f"Query preview: {query[:100]}...")

    try:
        graph = visualizer.visualize(query, "output/simple_join_ast", include_schema=True)
        print("✓ Successfully generated simple_join_ast.png")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_complex_query_with_validation():
    """Test complex query with schema validation"""
    print("\n" + "="*60)
    print("TEST 2: Complex Query with Schema Validation")
    print("="*60)

    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    # Test with a complex query that has some invalid columns
    query_with_errors = """
    SELECT
        c.customer_name,
        c.invalid_column,  -- This column doesn't exist
        COUNT(o.order_id) as order_count,
        SUM(o.total_amount) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.country = 'USA'
    GROUP BY c.customer_name, c.invalid_column
    """

    print("Visualizing query with intentional schema errors...")
    try:
        graph = visualizer.visualize(query_with_errors, "output/query_with_errors", include_schema=True)
        print("✓ Generated visualization with validation warnings")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_composable_subgraphs():
    """Test creating and combining multiple subgraphs"""
    print("\n" + "="*60)
    print("TEST 3: Composable Subgraphs")
    print("="*60)

    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    # Create multiple subgraphs
    print("Creating individual subgraphs...")

    # CTE query subgraph
    cte_query = """
    WITH customer_stats AS (
        SELECT customer_id, COUNT(*) as order_count
        FROM orders
        GROUP BY customer_id
    )
    SELECT * FROM customer_stats WHERE order_count > 5
    """
    cte_graph = visualizer.create_subgraph(cte_query, "cte_analysis", include_schema=True)
    print("✓ Created CTE analysis subgraph")

    # Aggregation query subgraph
    agg_query = QUERY_EXAMPLES["multi_join_aggregation"]
    agg_graph = visualizer.create_subgraph(agg_query, "aggregation_analysis", include_schema=True)
    print("✓ Created aggregation analysis subgraph")

    # Window function query subgraph
    window_query = QUERY_EXAMPLES["window_functions"]
    window_graph = visualizer.create_subgraph(window_query, "window_analysis", include_schema=True)
    print("✓ Created window function analysis subgraph")

    # Combine all subgraphs
    print("\nCombining subgraphs into single visualization...")
    try:
        combined = visualizer.combine_graphs(
            [cte_graph, agg_graph, window_graph],
            relationships=[
                ("node_0", "node_10", "feeds into"),
                ("node_10", "node_20", "transforms to")
            ],
            title="Combined SQL Analysis",
            output_file="output/combined_analysis"
        )
        print("✓ Successfully created combined_analysis.png")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_etl_pipeline_visualization():
    """Test ETL pipeline visualization with dependencies"""
    print("\n" + "="*60)
    print("TEST 4: ETL Pipeline Visualization")
    print("="*60)

    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    print("Visualizing ETL pipeline with 4 stages...")
    print("Stages: Extract → Transform → Aggregate → Load")

    try:
        pipeline_graph = visualizer.visualize_pipeline(
            ETL_PIPELINE,
            title="ETL Pipeline Flow",
            output_file="output/etl_pipeline",
            show_flow=True
        )
        print("✓ Successfully generated etl_pipeline.png")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_spark_df_integration():
    """Test integration with Spark DataFrame schema"""
    print("\n" + "="*60)
    print("TEST 5: Spark DataFrame Integration")
    print("="*60)

    # Create visualizer
    visualizer = SQLASTVisualizer()

    # Create schema from mock Spark DF
    print("Converting Spark DESCRIBE TABLE output to schema...")
    mock_spark_df = create_mock_spark_df()
    products_schema = SnowflakeSchema.from_spark_df("products", mock_spark_df)
    visualizer.add_schema(products_schema)
    print(f"✓ Added products schema with {len(products_schema.columns)} columns")

    # Test with a query using the products table
    query = """
    SELECT
        product_id,
        product_name,
        unit_price * stock_quantity as inventory_value
    FROM products
    WHERE category = 'Electronics'
        AND stock_quantity > 0
    ORDER BY inventory_value DESC
    """

    try:
        graph = visualizer.visualize(query, "output/spark_schema_test", include_schema=True)
        print("✓ Successfully visualized query with Spark-derived schema")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_all_query_types():
    """Test visualization of all query types"""
    print("\n" + "="*60)
    print("TEST 6: All Query Types")
    print("="*60)

    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    # Create output directory
    os.makedirs("output/query_types", exist_ok=True)

    successful = []
    failed = []

    for query_name, query_sql in QUERY_EXAMPLES.items():
        print(f"Testing {query_name}...", end=" ")
        try:
            output_path = f"output/query_types/{query_name}"
            graph = visualizer.visualize(query_sql, output_path, include_schema=True)
            successful.append(query_name)
            print("✓")
        except Exception as e:
            failed.append((query_name, str(e)))
            print(f"✗ ({str(e)[:50]}...)")

    print(f"\nResults: {len(successful)} successful, {len(failed)} failed")
    if failed:
        print("Failed queries:")
        for name, error in failed:
            print(f"  - {name}: {error[:100]}")


def test_custom_pipeline():
    """Test creating a custom analytical pipeline"""
    print("\n" + "="*60)
    print("TEST 7: Custom Analytical Pipeline")
    print("="*60)

    schemas = get_all_schemas()
    visualizer = SQLASTVisualizer(schemas)

    # Define a custom analytical pipeline
    custom_pipeline = [
        {
            "name": "Data_Quality_Check",
            "sql": """
                SELECT
                    COUNT(*) as total_records,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customers
                FROM orders
                WHERE order_date >= '2024-01-01'
            """
        },
        {
            "name": "Customer_Segmentation",
            "sql": """
                SELECT
                    customer_id,
                    COUNT(*) as order_count,
                    SUM(total_amount) as lifetime_value,
                    CASE
                        WHEN SUM(total_amount) > 10000 THEN 'VIP'
                        WHEN SUM(total_amount) > 5000 THEN 'Gold'
                        WHEN SUM(total_amount) > 1000 THEN 'Silver'
                        ELSE 'Bronze'
                    END as customer_tier
                FROM orders
                GROUP BY customer_id
            """,
            "depends_on": ["Data_Quality_Check"]
        },
        {
            "name": "Tier_Analysis",
            "sql": """
                SELECT
                    customer_tier,
                    COUNT(*) as customer_count,
                    AVG(lifetime_value) as avg_lifetime_value,
                    SUM(lifetime_value) as total_revenue
                FROM customer_segments
                GROUP BY customer_tier
                ORDER BY total_revenue DESC
            """,
            "depends_on": ["Customer_Segmentation"]
        }
    ]

    print("Creating custom analytical pipeline with 3 stages...")
    try:
        pipeline_graph = visualizer.visualize_pipeline(
            custom_pipeline,
            title="Customer Segmentation Analysis Pipeline",
            output_file="output/custom_pipeline",
            show_flow=True
        )
        print("✓ Successfully generated custom_pipeline.png")
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SQL AST VISUALIZER TEST SUITE")
    print("="*60)

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Run all tests
    tests = [
        test_single_query_visualization,
        test_complex_query_with_validation,
        test_composable_subgraphs,
        test_etl_pipeline_visualization,
        test_spark_df_integration,
        test_all_query_types,
        test_custom_pipeline
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n✗ Test {test_func.__name__} failed with error: {e}")

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print("\nCheck the 'output' directory for generated visualizations!")
    print("\nKey features demonstrated:")
    print("  1. Single query visualization with schema validation")
    print("  2. Error detection for invalid columns")
    print("  3. Composable subgraphs that can be combined")
    print("  4. ETL pipeline visualization with dependencies")
    print("  5. Spark DataFrame schema integration")
    print("  6. Support for complex SQL constructs (CTEs, window functions, etc.)")
    print("  7. Custom analytical pipelines")


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import sqlglot
        import graphviz
        print("✓ Required packages (sqlglot, graphviz) are available")
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Install with: pip install sqlglot graphviz")
        exit(1)

    # Check if graphviz binary is installed
    try:
        import subprocess
        subprocess.run(["dot", "-V"], capture_output=True, check=True)
        print("✓ Graphviz binary is installed")
    except:
        print("⚠ Graphviz binary not found. Install it:")
        print("  macOS: brew install graphviz")
        print("  Ubuntu: sudo apt-get install graphviz")
        print("  Windows: Download from https://graphviz.org/download/")

    main()