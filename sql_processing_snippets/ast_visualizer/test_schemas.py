"""
Test schemas for SQL AST Visualizer
Realistic e-commerce and analytics database schemas
"""

from sql_ast_visualizer import SnowflakeSchema, ColumnSchema


def create_ecommerce_schemas():
    """Create a complete e-commerce database schema"""

    # Users/Customers schema
    users_schema = SnowflakeSchema(
        table_name="users",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="name", data_type="varchar(255)"),
            ColumnSchema(column_name="email", data_type="varchar(255)"),
            ColumnSchema(column_name="created_at", data_type="timestamp"),
            ColumnSchema(column_name="updated_at", data_type="timestamp"),
            ColumnSchema(column_name="active", data_type="boolean"),
            ColumnSchema(column_name="customer_type", data_type="varchar(50)"),
        ]
    )

    customers_schema = SnowflakeSchema(
        table_name="customers",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="customer_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="customer_name", data_type="varchar(255)"),
            ColumnSchema(column_name="customer_email", data_type="varchar(255)"),
            ColumnSchema(column_name="customer_segment", data_type="varchar(50)"),
            ColumnSchema(column_name="country", data_type="varchar(100)"),
            ColumnSchema(column_name="city", data_type="varchar(100)"),
            ColumnSchema(column_name="created_date", data_type="date"),
            ColumnSchema(column_name="lifetime_value", data_type="decimal(10,2)"),
        ]
    )

    # Orders schema
    orders_schema = SnowflakeSchema(
        table_name="orders",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="order_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="customer_id", data_type="bigint"),
            ColumnSchema(column_name="user_id", data_type="bigint"),
            ColumnSchema(column_name="order_date", data_type="timestamp"),
            ColumnSchema(column_name="total_amount", data_type="decimal(10,2)"),
            ColumnSchema(column_name="status", data_type="varchar(50)"),
            ColumnSchema(column_name="shipping_address", data_type="text"),
            ColumnSchema(column_name="payment_method", data_type="varchar(50)"),
            ColumnSchema(column_name="created_at", data_type="timestamp"),
        ]
    )

    # Order Items schema
    order_items_schema = SnowflakeSchema(
        table_name="order_items",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="item_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="order_id", data_type="bigint"),
            ColumnSchema(column_name="product_id", data_type="bigint"),
            ColumnSchema(column_name="quantity", data_type="integer"),
            ColumnSchema(column_name="unit_price", data_type="decimal(10,2)"),
            ColumnSchema(column_name="discount", data_type="decimal(5,2)"),
            ColumnSchema(column_name="tax", data_type="decimal(10,2)"),
        ]
    )

    # Products schema
    products_schema = SnowflakeSchema(
        table_name="products",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="product_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="product_name", data_type="varchar(255)"),
            ColumnSchema(column_name="category", data_type="varchar(100)"),
            ColumnSchema(column_name="product_category", data_type="varchar(100)"),
            ColumnSchema(column_name="unit_price", data_type="decimal(10,2)"),
            ColumnSchema(column_name="cost", data_type="decimal(10,2)"),
            ColumnSchema(column_name="sku", data_type="varchar(100)"),
            ColumnSchema(column_name="stock_quantity", data_type="integer"),
            ColumnSchema(column_name="created_date", data_type="date"),
        ]
    )

    # Sales schema
    sales_schema = SnowflakeSchema(
        table_name="sales",
        database="ecommerce",
        schema="public",
        columns=[
            ColumnSchema(column_name="sale_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="product_id", data_type="bigint"),
            ColumnSchema(column_name="customer_id", data_type="bigint"),
            ColumnSchema(column_name="sale_date", data_type="date"),
            ColumnSchema(column_name="amount", data_type="decimal(10,2)"),
            ColumnSchema(column_name="sale_amount", data_type="decimal(10,2)"),
            ColumnSchema(column_name="quantity", data_type="integer"),
            ColumnSchema(column_name="region", data_type="varchar(50)"),
        ]
    )

    return {
        "users": users_schema,
        "customers": customers_schema,
        "orders": orders_schema,
        "order_items": order_items_schema,
        "products": products_schema,
        "sales": sales_schema,
    }


def create_hr_schemas():
    """Create HR/Employee database schemas"""

    # Employees schema
    employees_schema = SnowflakeSchema(
        table_name="employees",
        database="hr",
        schema="public",
        columns=[
            ColumnSchema(column_name="employee_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="employee_name", data_type="varchar(255)"),
            ColumnSchema(column_name="manager_id", data_type="bigint", nullable=True),
            ColumnSchema(column_name="department_id", data_type="bigint"),
            ColumnSchema(column_name="salary", data_type="decimal(10,2)"),
            ColumnSchema(column_name="hire_date", data_type="date"),
            ColumnSchema(column_name="job_title", data_type="varchar(100)"),
            ColumnSchema(column_name="email", data_type="varchar(255)"),
            ColumnSchema(column_name="phone", data_type="varchar(50)"),
        ]
    )

    # Departments schema
    departments_schema = SnowflakeSchema(
        table_name="departments",
        database="hr",
        schema="public",
        columns=[
            ColumnSchema(column_name="department_id", data_type="bigint", nullable=False),
            ColumnSchema(column_name="department_name", data_type="varchar(100)"),
            ColumnSchema(column_name="location", data_type="varchar(100)"),
            ColumnSchema(column_name="budget", data_type="decimal(12,2)"),
            ColumnSchema(column_name="manager_id", data_type="bigint"),
        ]
    )

    return {
        "employees": employees_schema,
        "departments": departments_schema,
    }


def create_staging_schemas():
    """Create staging/ETL schemas"""

    # Raw orders (for ETL pipeline)
    raw_orders_schema = SnowflakeSchema(
        table_name="raw_orders",
        database="staging",
        schema="raw",
        columns=[
            ColumnSchema(column_name="order_id", data_type="varchar(100)"),
            ColumnSchema(column_name="customer_id", data_type="varchar(100)"),
            ColumnSchema(column_name="order_date", data_type="varchar(100)"),
            ColumnSchema(column_name="total_amount", data_type="varchar(100)"),
            ColumnSchema(column_name="status", data_type="varchar(50)"),
            ColumnSchema(column_name="raw_data", data_type="json"),
        ]
    )

    # Staging orders
    staging_orders_schema = SnowflakeSchema(
        table_name="staging_orders",
        database="staging",
        schema="clean",
        columns=[
            ColumnSchema(column_name="order_id", data_type="bigint"),
            ColumnSchema(column_name="customer_id", data_type="bigint"),
            ColumnSchema(column_name="order_date", data_type="timestamp"),
            ColumnSchema(column_name="total_amount", data_type="decimal(10,2)"),
            ColumnSchema(column_name="status", data_type="varchar(50)"),
        ]
    )

    # Transformed orders
    transformed_orders_schema = SnowflakeSchema(
        table_name="transformed_orders",
        database="staging",
        schema="transformed",
        columns=[
            ColumnSchema(column_name="order_id", data_type="bigint"),
            ColumnSchema(column_name="customer_id", data_type="bigint"),
            ColumnSchema(column_name="customer_name", data_type="varchar(255)"),
            ColumnSchema(column_name="customer_segment", data_type="varchar(50)"),
            ColumnSchema(column_name="order_date", data_type="timestamp"),
            ColumnSchema(column_name="total_amount", data_type="decimal(10,2)"),
            ColumnSchema(column_name="order_value_category", data_type="varchar(20)"),
        ]
    )

    # Aggregated metrics
    aggregated_metrics_schema = SnowflakeSchema(
        table_name="aggregated_metrics",
        database="staging",
        schema="analytics",
        columns=[
            ColumnSchema(column_name="customer_segment", data_type="varchar(50)"),
            ColumnSchema(column_name="order_value_category", data_type="varchar(20)"),
            ColumnSchema(column_name="order_count", data_type="bigint"),
            ColumnSchema(column_name="total_revenue", data_type="decimal(12,2)"),
            ColumnSchema(column_name="avg_order_value", data_type="decimal(10,2)"),
        ]
    )

    # Customer segment summary (final table)
    customer_segment_summary_schema = SnowflakeSchema(
        table_name="customer_segment_summary",
        database="analytics",
        schema="reporting",
        columns=[
            ColumnSchema(column_name="customer_segment", data_type="varchar(50)"),
            ColumnSchema(column_name="order_value_category", data_type="varchar(20)"),
            ColumnSchema(column_name="order_count", data_type="bigint"),
            ColumnSchema(column_name="total_revenue", data_type="decimal(12,2)"),
            ColumnSchema(column_name="avg_order_value", data_type="decimal(10,2)"),
            ColumnSchema(column_name="created_at", data_type="timestamp"),
        ]
    )

    return {
        "raw_orders": raw_orders_schema,
        "staging_orders": staging_orders_schema,
        "transformed_orders": transformed_orders_schema,
        "aggregated_metrics": aggregated_metrics_schema,
        "customer_segment_summary": customer_segment_summary_schema,
    }


def get_all_schemas():
    """Get all schemas combined"""
    all_schemas = {}
    all_schemas.update(create_ecommerce_schemas())
    all_schemas.update(create_hr_schemas())
    all_schemas.update(create_staging_schemas())
    return all_schemas


def create_mock_spark_df():
    """
    Create a mock Spark DataFrame structure for testing
    This simulates what you'd get from DESCRIBE TABLE in Spark
    """
    class MockRow:
        def __init__(self, col_name, data_type, comment=None):
            self.col_name = col_name
            self.data_type = data_type
            self.comment = comment

        def __getitem__(self, key):
            return getattr(self, key)

        def get(self, key, default=None):
            return getattr(self, key, default)

    class MockSparkDF:
        def __init__(self, rows):
            self.rows = rows

        def collect(self):
            return self.rows

    # Example: Create a mock DESCRIBE TABLE result for products
    products_describe = MockSparkDF([
        MockRow("product_id", "bigint", "Primary key"),
        MockRow("product_name", "string", "Product display name"),
        MockRow("category", "string", "Product category"),
        MockRow("unit_price", "decimal(10,2)", "Price per unit"),
        MockRow("stock_quantity", "int", "Current stock level"),
    ])

    return products_describe


if __name__ == "__main__":
    # Test schema creation
    schemas = get_all_schemas()
    print(f"Created {len(schemas)} schemas:")
    for name, schema in schemas.items():
        print(f"  - {name}: {len(schema.columns)} columns")

    # Test Spark DF conversion
    mock_df = create_mock_spark_df()
    test_schema = SnowflakeSchema.from_spark_df("products", mock_df)
    print(f"\nTest Spark conversion: {test_schema.table_name} with {len(test_schema.columns)} columns")