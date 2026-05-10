# SKILL-15: Use CTEs to Break Complex Queries Into Steps

## When
A query requires multiple steps: filter, then aggregate, then rank, or join a derived result.

## Rule
Use a CTE (Common Table Expression) with WITH to make each step explicit and readable.
One CTE = one logical step. Name it clearly.

## Template
```sql
WITH filtered_orders AS (
    SELECT order_id, customer_id, total, ordered_at
    FROM orders
    WHERE ordered_at >= CURRENT_DATE - INTERVAL '90 days'
      AND status = 'delivered'
),
customer_totals AS (
    SELECT customer_id,
           COUNT(*)            AS order_count,
           ROUND(SUM(total), 2) AS total_spent
    FROM filtered_orders
    GROUP BY customer_id
)
SELECT
    c.name,
    ct.order_count,
    ct.total_spent
FROM customer_totals AS ct
INNER JOIN customers AS c ON c.id = ct.customer_id
ORDER BY ct.total_spent DESC
LIMIT 10;
```

## Benefits for a Small Model
- Each CTE is one simple thought. You do not have to hold the whole query in working memory.
- Easier to debug: you can test each CTE independently.
- Reduces nested subqueries which are harder to write correctly.

## PostgreSQL Note
PostgreSQL materialises CTEs by default before PostgreSQL 12. From v12+, the planner may inline them.
For large datasets, add MATERIALIZED or NOT MATERIALIZED to control this explicitly.

## Do Not
Write deeply nested subqueries when a CTE would be cleaner.
Nest more than 3 CTEs in one query.
