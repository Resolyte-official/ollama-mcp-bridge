# SKILL-16: Window Functions for Ranking and Running Totals

## When
User asks for: rankings, top-N per group, running totals, previous/next row comparisons.

## Key Window Functions

| Function            | Use                                         |
|---------------------|---------------------------------------------|
| ROW_NUMBER()        | Unique rank per row (no ties)               |
| RANK()              | Rank with gaps on ties (1,2,2,4)            |
| DENSE_RANK()        | Rank without gaps on ties (1,2,2,3)         |
| SUM() OVER(...)     | Running total                               |
| LAG(col, 1)         | Value from previous row                     |
| LEAD(col, 1)        | Value from next row                         |

## Top-N per group (e.g. top 3 products per category)
```sql
WITH ranked AS (
    SELECT
        product_name,
        category,
        total_sales,
        RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS rnk
    FROM product_sales
)
SELECT product_name, category, total_sales
FROM ranked
WHERE rnk <= 3;
```

## Running total
```sql
SELECT
    ordered_at,
    total,
    ROUND(SUM(total) OVER (ORDER BY ordered_at ROWS UNBOUNDED PRECEDING), 2) AS running_total
FROM orders
LIMIT 50;
```

## Month-over-month comparison
```sql
SELECT
    month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(revenue - LAG(revenue, 1) OVER (ORDER BY month), 2) AS change
FROM monthly_revenue
ORDER BY month DESC
LIMIT 12;
```

## Rule
Window functions do not collapse rows — they add a computed column.
Always wrap in a CTE if you need to filter on the window result.
