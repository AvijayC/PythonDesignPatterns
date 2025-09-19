# SQL AST Visualizer

A powerful SQL query visualization tool that creates Abstract Syntax Tree (AST) diagrams using sqlglot and graphviz. Perfect for understanding query structure, debugging complex SQL, and visualizing data pipelines.

## Features

- **AST Visualization**: Convert any SQL query into a visual tree structure
- **Composable Graphs**: Create individual query graphs and combine them later
- **Schema Validation**: Validate queries against your database schema
- **Pipeline Support**: Visualize ETL workflows with dependencies
- **Spark Integration**: Convert Spark DESCRIBE TABLE output to schemas
- **Color-Coded Nodes**: Different SQL constructs have unique colors for easy identification

## Installation

```bash
# Install required packages
pip install sqlglot graphviz pydantic

# Install graphviz binary (required for rendering)
# macOS:
brew install graphviz

# Ubuntu/Debian:
sudo apt-get install graphviz

# Windows:
# Download from https://graphviz.org/download/
```

## Quick Start

```python
from sql_ast_visualizer import SQLASTVisualizer, SnowflakeSchema, ColumnSchema

# Create a simple schema
users_schema = SnowflakeSchema(
    table_name="users",
    columns=[
        ColumnSchema(column_name="id", data_type="bigint"),
        ColumnSchema(column_name="name", data_type="varchar"),
        ColumnSchema(column_name="email", data_type="varchar")
    ]
)

# Initialize visualizer
viz = SQLASTVisualizer({"users": users_schema})

# Visualize a query
query = "SELECT id, name FROM users WHERE email LIKE '%@example.com'"
viz.visualize(query, "output/my_query")
```

## Advanced Usage

### 1. Composable Subgraphs

```python
# Create individual subgraphs
graph1 = viz.create_subgraph(query1, "analysis_1")
graph2 = viz.create_subgraph(query2, "analysis_2")

# Combine with relationships
combined = viz.combine_graphs(
    [graph1, graph2],
    relationships=[("node_1", "node_5", "feeds into")],
    output_file="combined_analysis"
)
```

### 2. ETL Pipeline Visualization

```python
pipeline = [
    {"name": "Extract", "sql": "SELECT * FROM raw_data"},
    {"name": "Transform", "sql": "SELECT id, UPPER(name) FROM staging", "depends_on": ["Extract"]},
    {"name": "Load", "sql": "INSERT INTO final SELECT * FROM transformed", "depends_on": ["Transform"]}
]

viz.visualize_pipeline(pipeline, "ETL Pipeline", "etl_flow")
```

### 3. Spark DataFrame Integration

```python
# Convert Spark DESCRIBE TABLE output
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
describe_df = spark.sql("DESCRIBE TABLE products")

# Convert to schema
schema = SnowflakeSchema.from_spark_df("products", describe_df)
viz.add_schema(schema)
```

## File Structure

- `sql_ast_visualizer.py` - Main visualizer class and Pydantic models
- `sql_query_examples.py` - Collection of complex SQL queries for testing
- `test_schemas.py` - Realistic database schemas (e-commerce, HR, ETL)
- `test_visualizer.py` - Comprehensive test suite demonstrating all features

## Running Tests

```bash
python test_visualizer.py
```

This will generate various visualizations in the `output/` directory:
- Single query ASTs
- Combined multi-query analysis
- ETL pipeline flows
- Schema validation examples

## Node Color Legend

| Color | SQL Construct |
|-------|--------------|
| Light Green | SELECT |
| Light Yellow | WHERE/HAVING |
| Light Coral | JOIN |
| Light Gray | TABLE |
| White | COLUMN |
| Light Pink | GROUP BY |
| Lavender | ORDER BY |
| Light Cyan | LIMIT |
| Plum | SUBQUERY |
| Light Steel Blue | CTE/WITH |
| Khaki | WINDOW |
| Moccasin | CASE |
| Light Salmon | Aggregate Functions |

## Use Cases

1. **Query Optimization**: Visualize query structure to identify optimization opportunities
2. **Documentation**: Generate visual documentation for complex queries
3. **Debugging**: Quickly understand query execution flow
4. **Learning**: Teach SQL concepts through visual representation
5. **Code Review**: Share query visualizations for better code reviews
6. **Pipeline Management**: Track data flow through ETL processes

## Examples

See `sql_query_examples.py` for complex query examples including:
- Multi-table joins with aggregations
- Recursive CTEs
- Window functions
- Subqueries
- Set operations (UNION, INTERSECT)
- CASE statements
- Pivot simulations
- Analytical dashboards

## Contributing

Feel free to extend the visualizer with additional features:
- Add new node colors for specific SQL constructs
- Implement query optimization suggestions
- Add support for database-specific SQL dialects
- Create interactive visualizations