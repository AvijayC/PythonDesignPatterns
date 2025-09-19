"""
SQL AST Visualizer with Composable Graphs
Visualizes SQL queries as Abstract Syntax Trees using sqlglot and graphviz
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import sqlglot
from sqlglot import parse_one, exp
import graphviz
from dataclasses import dataclass


class ColumnSchema(BaseModel):
    """Schema for a single column"""
    column_name: str = Field(alias="col_name")
    data_type: str
    comment: Optional[str] = None
    nullable: Optional[bool] = True

    class Config:
        populate_by_name = True


class SnowflakeSchema(BaseModel):
    """Interface for table schema information"""
    table_name: str
    columns: List[ColumnSchema]
    database: Optional[str] = None
    schema: Optional[str] = None

    @classmethod
    def from_spark_df(cls, table_name: str, describe_df) -> 'SnowflakeSchema':
        """
        Convert PySpark DESCRIBE TABLE output to SnowflakeSchema

        Args:
            table_name: Name of the table
            describe_df: PySpark DataFrame from DESCRIBE TABLE
        """
        # Collect the describe output
        rows = describe_df.collect()

        # Convert to list of column schemas
        columns = []
        for row in rows:
            # Skip partition info rows if present
            if row['col_name'] and not row['col_name'].startswith('#'):
                columns.append(ColumnSchema(
                    column_name=row['col_name'],
                    data_type=row['data_type'],
                    comment=row.get('comment')
                ))

        return cls(table_name=table_name, columns=columns)

    def get_column(self, column_name: str) -> Optional[ColumnSchema]:
        """Get column schema by name"""
        for col in self.columns:
            if col.column_name.lower() == column_name.lower():
                return col
        return None


@dataclass
class GraphNode:
    """Represents a node in the AST graph"""
    id: str
    node_type: str
    sql_snippet: str
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    schema_info: Optional[Dict[str, Any]] = None


class SQLASTVisualizer:
    """Visualize SQL queries as AST with schema validation and graph composition"""

    def __init__(self, schemas: Optional[Dict[str, SnowflakeSchema]] = None):
        """
        Initialize with optional schema information

        Args:
            schemas: Dict mapping table names to SnowflakeSchema objects
        """
        self.schemas = schemas or {}
        self.node_colors = {
            'Select': '#90EE90',      # Light green
            'Where': '#FFFFE0',       # Light yellow
            'Join': '#F08080',        # Light coral
            'Table': '#D3D3D3',       # Light gray
            'Column': '#FFFFFF',      # White
            'Group': '#FFB6C1',       # Light pink
            'Having': '#FAFAD2',      # Light goldenrod
            'Order': '#E6E6FA',       # Lavender
            'Limit': '#E0FFFF',       # Light cyan
            'Subquery': '#DDA0DD',    # Plum
            'CTE': '#B0C4DE',         # Light steel blue
            'Window': '#F0E68C',      # Khaki
            'Case': '#FFE4B5',        # Moccasin
            'AggFunc': '#FFA07A',     # Light salmon
            'Union': '#87CEEB',       # Sky blue
            'Intersect': '#98D8C8',   # Mint
            'Except': '#F7DC6F',      # Light gold
        }
        self.node_counter = 0
        self.nodes_registry = {}  # Track nodes for cross-referencing

    def add_schema(self, schema: SnowflakeSchema) -> None:
        """Add or update schema for a table"""
        self.schemas[schema.table_name.lower()] = schema

    def add_schemas(self, schemas: List[SnowflakeSchema]) -> None:
        """Add multiple schemas at once"""
        for schema in schemas:
            self.add_schema(schema)

    def validate_columns(self, ast: exp.Expression) -> Dict[str, List[str]]:
        """
        Validate columns in AST against known schemas

        Returns:
            Dict mapping table names to lists of invalid column names
        """
        validation_errors = {}

        for column in ast.find_all(exp.Column):
            table_name = self._resolve_table_for_column(column, ast)
            if table_name and table_name.lower() in self.schemas:
                schema = self.schemas[table_name.lower()]
                column_name = column.name

                # Check if column exists in schema
                if not schema.get_column(column_name):
                    if table_name not in validation_errors:
                        validation_errors[table_name] = []
                    validation_errors[table_name].append(column_name)

        return validation_errors

    def _resolve_table_for_column(self, column: exp.Column, ast: exp.Expression) -> Optional[str]:
        """Resolve which table a column belongs to"""
        # If column has explicit table reference
        if column.table:
            # Handle aliased tables
            for table in ast.find_all(exp.Table):
                if table.alias and table.alias == column.table:
                    return table.name
            return column.table

        # Otherwise, try to infer from FROM clause (first table as default)
        for table in ast.find_all(exp.Table):
            return table.name

        return None

    def create_subgraph(self, query: str, subgraph_name: str = None,
                       include_schema: bool = True,
                       validate: bool = True) -> graphviz.Digraph:
        """
        Create a subgraph that can be combined with other graphs

        Args:
            query: SQL query string
            subgraph_name: Unique name for this subgraph
            include_schema: Whether to include schema info in visualization
            validate: Whether to validate columns against schema

        Returns:
            graphviz.Digraph subgraph object
        """
        ast = parse_one(query)

        # Validate if requested
        validation_errors = {}
        if validate and self.schemas:
            validation_errors = self.validate_columns(ast)

        # Create subgraph with unique name
        if not subgraph_name:
            subgraph_name = f"cluster_{self.node_counter}"
            self.node_counter += 1

        subgraph = graphviz.Digraph(name=subgraph_name)

        # Style the subgraph
        query_preview = query.replace('\n', ' ')[:100] + ('...' if len(query) > 100 else '')
        subgraph.attr(label=f"Query: {query_preview}")
        subgraph.attr(style='rounded,filled', bgcolor='#f9f9f9', color='#666666')

        # Add validation errors if any
        if validation_errors:
            error_msg = "⚠️ Invalid columns: "
            for table, cols in validation_errors.items():
                error_msg += f"{table}({', '.join(cols)}) "
            subgraph.node(f"{subgraph_name}_error", error_msg,
                         shape='note', fillcolor='#FFD700', style='filled')

        # Build the tree in this subgraph
        root_id = self._add_node_recursive(ast, subgraph, None, include_schema)

        # Store root node for potential cross-referencing
        self.nodes_registry[subgraph_name] = root_id

        return subgraph

    def _add_node_recursive(self, node: exp.Expression, graph: graphviz.Digraph,
                          parent_id: Optional[str], include_schema: bool) -> str:
        """Recursively add nodes to graph"""
        # Generate unique node ID
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        # Create label based on node type
        node_type = node.__class__.__name__
        sql_snippet = self._get_node_snippet(node)
        label_parts = [node_type]

        if sql_snippet:
            label_parts.append(sql_snippet)

        # Add schema info for specific node types
        if include_schema:
            schema_info = self._get_schema_info(node)
            if schema_info:
                label_parts.append(schema_info)

        label = '\\n'.join(label_parts)

        # Get color for node type
        color = self.node_colors.get(node_type, '#E6E6E6')

        # Special styling for certain nodes
        shape = 'box'
        style = 'rounded,filled'

        if isinstance(node, exp.Subquery):
            shape = 'box3d'
        elif isinstance(node, (exp.CTE, exp.With)):
            shape = 'component'
        elif isinstance(node, exp.AggFunc):
            shape = 'ellipse'

        # Add node to graph
        graph.node(node_id, label, fillcolor=color, shape=shape, style=style)

        # Connect to parent if exists
        if parent_id:
            graph.edge(parent_id, node_id)

        # Process children
        for child in node.iter_expressions():
            self._add_node_recursive(child, graph, node_id, include_schema)

        return node_id

    def _get_node_snippet(self, node: exp.Expression) -> str:
        """Get a readable snippet for the node"""
        try:
            sql = node.sql()

            # Special handling for different node types
            if isinstance(node, exp.Select):
                # Just show SELECT without the full query
                return "SELECT ..."
            elif isinstance(node, exp.From):
                return "FROM ..."
            elif isinstance(node, exp.Where):
                return "WHERE ..."
            elif isinstance(node, exp.Group):
                return "GROUP BY ..."
            elif isinstance(node, exp.Order):
                return "ORDER BY ..."
            elif isinstance(node, exp.Table):
                alias = f" AS {node.alias}" if node.alias else ""
                return f"{node.name}{alias}"
            elif isinstance(node, exp.Column):
                table_ref = f"{node.table}." if node.table else ""
                return f"{table_ref}{node.name}"
            elif isinstance(node, exp.Literal):
                return str(node.this)[:20]
            else:
                # Truncate long SQL
                if len(sql) > 30:
                    return sql[:30] + "..."
                return sql
        except:
            return ""

    def _get_schema_info(self, node: exp.Expression) -> Optional[str]:
        """Get schema information for node if available"""
        if isinstance(node, exp.Table):
            table_name = node.name.lower()
            if table_name in self.schemas:
                schema = self.schemas[table_name]
                return f"[{len(schema.columns)} columns]"
        elif isinstance(node, exp.Column):
            # Could add column type info here if needed
            pass
        return None

    @staticmethod
    def combine_graphs(graphs: List[graphviz.Digraph],
                       relationships: List[Tuple[str, str, str]] = None,
                       title: str = "Combined SQL Analysis",
                       output_file: str = 'combined_ast') -> graphviz.Digraph:
        """
        Combine multiple graphs into one visualization

        Args:
            graphs: List of graphviz.Digraph objects to combine
            relationships: List of (from_node, to_node, label) tuples for cross-graph edges
            title: Title for the combined graph
            output_file: Output filename

        Returns:
            Combined graphviz.Digraph
        """
        # Create parent graph
        combined = graphviz.Digraph('Combined_SQL_AST', format='png')
        combined.attr(label=title, fontsize='16', fontweight='bold')
        combined.attr(rankdir='TB', bgcolor='white')
        combined.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        combined.attr('edge', fontname='Arial', fontsize='10')

        # Add all subgraphs
        for graph in graphs:
            combined.subgraph(graph)

        # Add cross-graph relationships if any
        if relationships:
            for from_node, to_node, label in relationships:
                combined.edge(from_node, to_node, label=label,
                            style='dashed', color='red', fontcolor='red')

        combined.render(output_file, view=True, cleanup=True)
        return combined

    def visualize_pipeline(self, queries: List[Dict[str, str]],
                          title: str = "SQL Pipeline",
                          output_file: str = 'pipeline_ast',
                          show_flow: bool = True) -> graphviz.Digraph:
        """
        Visualize multiple queries as a pipeline

        Args:
            queries: List of dicts with 'name' and 'sql' keys, optionally 'depends_on'
            title: Title for the pipeline visualization
            output_file: Output filename
            show_flow: Whether to show flow between queries

        Returns:
            Combined pipeline visualization
        """
        subgraphs = []
        query_roots = {}

        for i, query_info in enumerate(queries):
            name = query_info.get('name', f'Query_{i}')
            sql = query_info['sql']

            # Create subgraph for each query
            subgraph_name = f"cluster_{name.replace(' ', '_')}"
            subgraph = self.create_subgraph(sql, subgraph_name, True)
            subgraphs.append(subgraph)

            # Track root nodes for dependencies
            query_roots[name] = self.nodes_registry.get(subgraph_name)

        # Build relationships based on dependencies or sequential flow
        relationships = []
        if show_flow:
            for i, query_info in enumerate(queries):
                name = query_info.get('name', f'Query_{i}')

                # Check for explicit dependencies
                if 'depends_on' in query_info:
                    for dep in query_info['depends_on']:
                        if dep in query_roots and name in query_roots:
                            relationships.append(
                                (query_roots[dep], query_roots[name], "feeds")
                            )
                # Otherwise, create sequential flow
                elif i > 0:
                    prev_name = queries[i-1].get('name', f'Query_{i-1}')
                    if prev_name in query_roots and name in query_roots:
                        relationships.append(
                            (query_roots[prev_name], query_roots[name], "then")
                        )

        # Combine all subgraphs
        combined = self.combine_graphs(subgraphs, relationships, title, output_file)
        return combined

    def visualize(self, query: str, output_file: str = 'sql_ast',
                 include_schema: bool = True) -> graphviz.Digraph:
        """
        Simple method to visualize a single query

        Args:
            query: SQL query string
            output_file: Output filename
            include_schema: Whether to include schema info

        Returns:
            graphviz.Digraph object
        """
        # Reset node counter for single visualizations
        self.node_counter = 0
        self.nodes_registry = {}

        # Create a single graph (not a subgraph)
        dot = graphviz.Digraph('SQL_AST', format='png')
        dot.attr(rankdir='TB', bgcolor='white')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')

        # Parse and validate
        ast = parse_one(query)
        validation_errors = {}
        if include_schema and self.schemas:
            validation_errors = self.validate_columns(ast)

        # Add validation errors if any
        if validation_errors:
            error_msg = "⚠️ Invalid columns:\\n"
            for table, cols in validation_errors.items():
                error_msg += f"  {table}: {', '.join(cols)}\\n"
            dot.node('validation_error', error_msg, shape='note',
                    fillcolor='#FFD700', style='filled')

        # Build the tree
        self._add_node_recursive(ast, dot, None, include_schema)

        # Render
        dot.render(output_file, view=True, cleanup=True)
        return dot