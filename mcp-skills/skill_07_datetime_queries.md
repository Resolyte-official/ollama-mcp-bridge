# SKILL-07: Date and Time Queries in PostgreSQL

## When
Any query involving dates, times, ranges, or relative periods.

## Key PostgreSQL Date Functions

| Need                    | Function / Expression                        |
|-------------------------|----------------------------------------------|
| Today's date            | CURRENT_DATE                                 |
| Now (with time)         | NOW()                                        |
| Subtract interval       | NOW() - INTERVAL '7 days'                    |
| Extract part            | EXTRACT(YEAR FROM created_at)                |
| Truncate to month       | DATE_TRUNC('month', created_at)              |
| Format for display      | TO_CHAR(created_at, 'YYYY-MM-DD')            |

## Common Patterns

### Records from the last N days
```sql
SELECT order_id, total
FROM orders
WHERE ordered_at >= CURRENT_DATE - INTERVAL '30 days'
LIMIT 50;
```

### Group by month
```sql
SELECT DATE_TRUNC('month', ordered_at) AS month,
       COUNT(*) AS order_count,
       SUM(total) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1 DESC;
```

### Between two dates
```sql
SELECT id, name
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-03-31';
```

## Watch Out
- Always use ISO 8601 format for date literals: 'YYYY-MM-DD'.
- If the column is TIMESTAMPTZ, comparisons are timezone-aware.
- DATE_TRUNC returns a TIMESTAMP, not a DATE — use ::date to cast if needed.
