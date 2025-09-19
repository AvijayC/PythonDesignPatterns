"""
Complex SQL Query Examples for Testing AST Visualization
"""

# Simple queries
SIMPLE_SELECT = """
SELECT id, name, email
FROM users
WHERE active = true
"""

SIMPLE_JOIN = """
SELECT u.name, o.order_date, o.total_amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
"""

# Complex queries with multiple joins
MULTI_JOIN_AGGREGATION = """
SELECT
    c.customer_name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.quantity * p.unit_price) as total_spent,
    AVG(oi.quantity * p.unit_price) as avg_order_value,
    MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE c.country = 'USA'
    AND o.order_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name
HAVING SUM(oi.quantity * p.unit_price) > 1000
ORDER BY total_spent DESC
LIMIT 100
"""

# CTE (Common Table Expression) query
CTE_RECURSIVE = """
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor member: top-level employees
    SELECT
        employee_id,
        employee_name,
        manager_id,
        department_id,
        1 as level,
        CAST(employee_name AS VARCHAR(1000)) as path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive member: employees with managers
    SELECT
        e.employee_id,
        e.employee_name,
        e.manager_id,
        e.department_id,
        eh.level + 1,
        CONCAT(eh.path, ' -> ', e.employee_name) as path
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
    WHERE eh.level < 10
),
department_stats AS (
    SELECT
        d.department_name,
        COUNT(DISTINCT e.employee_id) as employee_count,
        AVG(e.salary) as avg_salary
    FROM departments d
    LEFT JOIN employees e ON d.department_id = e.department_id
    GROUP BY d.department_id, d.department_name
)
SELECT
    eh.employee_name,
    eh.level,
    eh.path,
    d.department_name,
    ds.employee_count as dept_size,
    ds.avg_salary as dept_avg_salary
FROM employee_hierarchy eh
JOIN departments d ON eh.department_id = d.department_id
JOIN department_stats ds ON d.department_name = ds.department_name
WHERE eh.level <= 5
ORDER BY eh.level, eh.employee_name
"""

# Window functions query
WINDOW_FUNCTIONS = """
SELECT
    product_category,
    product_name,
    sale_date,
    sale_amount,
    -- Running total within category
    SUM(sale_amount) OVER (
        PARTITION BY product_category
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total,
    -- Rank within category
    RANK() OVER (
        PARTITION BY product_category
        ORDER BY sale_amount DESC
    ) as sales_rank,
    -- Percentage of category total
    sale_amount / SUM(sale_amount) OVER (
        PARTITION BY product_category
    ) * 100 as pct_of_category,
    -- Lead and lag for comparison
    LAG(sale_amount, 1) OVER (
        PARTITION BY product_category
        ORDER BY sale_date
    ) as prev_sale,
    LEAD(sale_amount, 1) OVER (
        PARTITION BY product_category
        ORDER BY sale_date
    ) as next_sale
FROM sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
"""

# Subquery examples
COMPLEX_SUBQUERIES = """
SELECT
    d.department_name,
    d.location,
    (
        SELECT COUNT(*)
        FROM employees e
        WHERE e.department_id = d.department_id
            AND e.salary > (
                SELECT AVG(salary)
                FROM employees e2
                WHERE e2.department_id = e.department_id
            )
    ) as above_avg_employees,
    (
        SELECT MAX(e.salary)
        FROM employees e
        WHERE e.department_id = d.department_id
    ) as max_salary,
    (
        SELECT STRING_AGG(e.employee_name, ', ')
        FROM (
            SELECT employee_name
            FROM employees
            WHERE department_id = d.department_id
            ORDER BY salary DESC
            LIMIT 3
        ) e
    ) as top_earners
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.department_id
        AND e.hire_date >= '2024-01-01'
)
"""

# UNION and set operations
SET_OPERATIONS = """
WITH high_value_customers AS (
    SELECT
        customer_id,
        'High Value' as customer_type,
        total_purchases
    FROM (
        SELECT
            c.customer_id,
            SUM(o.total_amount) as total_purchases
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_date >= DATEADD(month, -12, GETDATE())
        GROUP BY c.customer_id
        HAVING SUM(o.total_amount) > 10000
    ) t1
),
frequent_customers AS (
    SELECT
        customer_id,
        'Frequent' as customer_type,
        order_count as total_purchases
    FROM (
        SELECT
            customer_id,
            COUNT(*) as order_count
        FROM orders
        WHERE order_date >= DATEADD(month, -6, GETDATE())
        GROUP BY customer_id
        HAVING COUNT(*) > 20
    ) t2
)
SELECT * FROM high_value_customers
UNION
SELECT * FROM frequent_customers
UNION
SELECT
    customer_id,
    'New' as customer_type,
    0 as total_purchases
FROM customers
WHERE created_date >= DATEADD(month, -1, GETDATE())
    AND customer_id NOT IN (
        SELECT customer_id FROM high_value_customers
        UNION
        SELECT customer_id FROM frequent_customers
    )
ORDER BY customer_type, total_purchases DESC
"""

# CASE statements and conditional logic
CASE_STATEMENTS = """
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount,
    CASE
        WHEN o.total_amount >= 1000 THEN 'Large'
        WHEN o.total_amount >= 500 THEN 'Medium'
        WHEN o.total_amount >= 100 THEN 'Small'
        ELSE 'Micro'
    END as order_size,
    CASE
        WHEN DATEDIFF(day, o.order_date, GETDATE()) <= 7 THEN 'Recent'
        WHEN DATEDIFF(day, o.order_date, GETDATE()) <= 30 THEN 'This Month'
        WHEN DATEDIFF(day, o.order_date, GETDATE()) <= 90 THEN 'This Quarter'
        ELSE 'Older'
    END as recency,
    CASE
        WHEN c.customer_type = 'Premium'
            AND o.total_amount > 500 THEN o.total_amount * 0.9
        WHEN c.customer_type = 'Regular'
            AND o.total_amount > 1000 THEN o.total_amount * 0.95
        ELSE o.total_amount
    END as discounted_amount,
    CASE
        WHEN EXISTS (
            SELECT 1 FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = o.order_id
                AND p.category = 'Electronics'
        ) THEN 'Electronics Order'
        ELSE 'Other'
    END as order_category
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status IN ('completed', 'shipped')
"""

# Pivot/unpivot simulation
PIVOT_SIMULATION = """
SELECT
    product_id,
    product_name,
    MAX(CASE WHEN month_num = 1 THEN sales_amount ELSE 0 END) as jan_sales,
    MAX(CASE WHEN month_num = 2 THEN sales_amount ELSE 0 END) as feb_sales,
    MAX(CASE WHEN month_num = 3 THEN sales_amount ELSE 0 END) as mar_sales,
    MAX(CASE WHEN month_num = 4 THEN sales_amount ELSE 0 END) as apr_sales,
    MAX(CASE WHEN month_num = 5 THEN sales_amount ELSE 0 END) as may_sales,
    MAX(CASE WHEN month_num = 6 THEN sales_amount ELSE 0 END) as jun_sales,
    SUM(sales_amount) as total_sales,
    AVG(sales_amount) as avg_monthly_sales
FROM (
    SELECT
        p.product_id,
        p.product_name,
        MONTH(s.sale_date) as month_num,
        SUM(s.amount) as sales_amount
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    WHERE YEAR(s.sale_date) = 2024
    GROUP BY p.product_id, p.product_name, MONTH(s.sale_date)
) monthly_sales
GROUP BY product_id, product_name
HAVING SUM(sales_amount) > 1000
ORDER BY total_sales DESC
"""

# Complex analytical query with multiple CTEs
ANALYTICAL_DASHBOARD = """
WITH date_range AS (
    SELECT
        DATEADD(day, number, '2024-01-01') as analysis_date
    FROM master.dbo.spt_values
    WHERE type = 'P'
        AND DATEADD(day, number, '2024-01-01') <= '2024-12-31'
),
daily_metrics AS (
    SELECT
        dr.analysis_date,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        COUNT(o.order_id) as order_count,
        SUM(o.total_amount) as revenue,
        AVG(o.total_amount) as avg_order_value
    FROM date_range dr
    LEFT JOIN orders o ON CAST(o.order_date AS DATE) = dr.analysis_date
    GROUP BY dr.analysis_date
),
moving_averages AS (
    SELECT
        analysis_date,
        unique_customers,
        order_count,
        revenue,
        AVG(revenue) OVER (
            ORDER BY analysis_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as revenue_7day_avg,
        AVG(revenue) OVER (
            ORDER BY analysis_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) as revenue_30day_avg
    FROM daily_metrics
),
yoy_comparison AS (
    SELECT
        m1.analysis_date,
        m1.revenue as current_revenue,
        m2.revenue as previous_year_revenue,
        CASE
            WHEN m2.revenue > 0
            THEN ((m1.revenue - m2.revenue) / m2.revenue) * 100
            ELSE NULL
        END as yoy_growth_pct
    FROM daily_metrics m1
    LEFT JOIN daily_metrics m2
        ON m2.analysis_date = DATEADD(year, -1, m1.analysis_date)
)
SELECT
    ma.analysis_date,
    ma.unique_customers,
    ma.order_count,
    ma.revenue,
    ma.revenue_7day_avg,
    ma.revenue_30day_avg,
    yoy.yoy_growth_pct,
    CASE
        WHEN ma.revenue > ma.revenue_7day_avg * 1.2 THEN 'Peak Day'
        WHEN ma.revenue < ma.revenue_7day_avg * 0.8 THEN 'Low Day'
        ELSE 'Normal'
    END as day_classification
FROM moving_averages ma
JOIN yoy_comparison yoy ON ma.analysis_date = yoy.analysis_date
WHERE ma.analysis_date >= '2024-02-01'
ORDER BY ma.analysis_date
"""

# Query collection for easy access
QUERY_EXAMPLES = {
    "simple_select": SIMPLE_SELECT,
    "simple_join": SIMPLE_JOIN,
    "multi_join_aggregation": MULTI_JOIN_AGGREGATION,
    "cte_recursive": CTE_RECURSIVE,
    "window_functions": WINDOW_FUNCTIONS,
    "complex_subqueries": COMPLEX_SUBQUERIES,
    "set_operations": SET_OPERATIONS,
    "case_statements": CASE_STATEMENTS,
    "pivot_simulation": PIVOT_SIMULATION,
    "analytical_dashboard": ANALYTICAL_DASHBOARD
}

# Pipeline example - ETL queries that depend on each other
ETL_PIPELINE = [
    {
        "name": "Extract_Raw_Data",
        "sql": """
            SELECT
                order_id,
                customer_id,
                order_date,
                total_amount,
                status
            FROM raw_orders
            WHERE order_date >= '2024-01-01'
                AND status != 'cancelled'
        """
    },
    {
        "name": "Transform_Enrich",
        "sql": """
            SELECT
                o.order_id,
                o.customer_id,
                c.customer_name,
                c.customer_segment,
                o.order_date,
                o.total_amount,
                CASE
                    WHEN o.total_amount >= 1000 THEN 'High'
                    WHEN o.total_amount >= 500 THEN 'Medium'
                    ELSE 'Low'
                END as order_value_category
            FROM staging_orders o
            JOIN customers c ON o.customer_id = c.customer_id
        """,
        "depends_on": ["Extract_Raw_Data"]
    },
    {
        "name": "Aggregate_Metrics",
        "sql": """
            SELECT
                customer_segment,
                order_value_category,
                COUNT(*) as order_count,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value
            FROM transformed_orders
            GROUP BY customer_segment, order_value_category
        """,
        "depends_on": ["Transform_Enrich"]
    },
    {
        "name": "Load_Summary",
        "sql": """
            INSERT INTO customer_segment_summary
            SELECT
                customer_segment,
                order_value_category,
                order_count,
                total_revenue,
                avg_order_value,
                CURRENT_TIMESTAMP as created_at
            FROM aggregated_metrics
            WHERE total_revenue > 0
        """,
        "depends_on": ["Aggregate_Metrics"]
    }
]