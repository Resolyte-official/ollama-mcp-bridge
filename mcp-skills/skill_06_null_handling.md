# SKILL-06: Handle NULL Values Correctly

## When
Any query that filters, displays, or computes on columns that may be NULL.

## Rules

### Filtering NULLs
Use IS NULL or IS NOT NULL. Never use = NULL or != NULL.

```sql
-- Correct
SELECT id, email FROM customers WHERE phone IS NULL;

-- Wrong — returns no rows, silently
SELECT id, email FROM customers WHERE phone = NULL;
```

### Displaying NULLs to the User
Replace NULLs with a readable fallback using COALESCE.

```sql
SELECT name, COALESCE(phone, 'not provided') AS phone
FROM customers;
```

### Aggregations and NULLs
COUNT(*) counts all rows including NULLs.
COUNT(column) skips NULLs.
SUM, AVG, MIN, MAX all ignore NULLs automatically.

Tell the user if a column has NULLs that affected the aggregation:
```sql
SELECT COUNT(*) AS total_rows,
       COUNT(phone) AS rows_with_phone
FROM customers;
```

### Sorting with NULLs
In PostgreSQL, NULLs sort last in ASC and first in DESC by default.
Use NULLS LAST or NULLS FIRST to be explicit:
```sql
SELECT name, score
FROM results
ORDER BY score DESC NULLS LAST;
```
