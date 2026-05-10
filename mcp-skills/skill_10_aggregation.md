# SKILL-10: Aggregation Queries

## When
User asks for totals, averages, counts, breakdowns, or summaries.

## Core Aggregation Functions in PostgreSQL

| Function     | Returns                          |
|--------------|----------------------------------|
| COUNT(*)     | Total row count                  |
| COUNT(col)   | Count of non-NULL values         |
| SUM(col)     | Sum of numeric column            |
| AVG(col)     | Average (returns numeric/float)  |
| MIN(col)     | Smallest value                   |
| MAX(col)     | Largest value                    |
| ROUND(x, 2)  | Round to 2 decimal places        |

## Template: Group by one dimension
```sql
SELECT
    status,
    COUNT(*)            AS order_count,
    ROUND(SUM(total), 2) AS revenue
FROM orders
GROUP BY status
ORDER BY revenue DESC;
```

## Template: Group by time period
```sql
SELECT
    DATE_TRUNC('month', ordered_at) AS month,
    COUNT(*)                         AS orders,
    ROUND(AVG(total), 2)             AS avg_order_value
FROM orders
GROUP BY 1
ORDER BY 1 DESC
LIMIT 12;
```

## Rules
- Every column in SELECT that is not an aggregate must appear in GROUP BY.
- Use HAVING to filter on aggregate results, not WHERE.
- HAVING example: `HAVING COUNT(*) > 10`
- Always ROUND monetary/decimal results to 2 decimal places for display.
- Aggregations rarely need LIMIT — they already return one row per group.
