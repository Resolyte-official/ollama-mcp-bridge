# SKILL-22: PostgreSQL-Specific Syntax to Always Use

## When
Writing any query. PostgreSQL has specific syntax that differs from standard SQL or other databases.

## Always Use These PostgreSQL Idioms

### String concatenation
```sql
-- PostgreSQL
SELECT first_name || ' ' || last_name AS full_name FROM customers;
-- Not: CONCAT() is valid but || is idiomatic
```

### Boolean literals
```sql
WHERE is_active = TRUE
WHERE is_active = FALSE
-- Not: WHERE is_active = 1
```

### Returning the current date/time
```sql
CURRENT_DATE        -- date only: 2024-11-10
NOW()               -- timestamp with timezone
CURRENT_TIMESTAMP   -- same as NOW()
```

### Case-insensitive search
```sql
WHERE name ILIKE '%alice%'
-- Not: LOWER(name) LIKE '%alice%'  (works but slower)
```

### Array columns (if present)
```sql
WHERE 'admin' = ANY(roles)       -- check if value is in array
WHERE roles @> ARRAY['admin']    -- array contains
```

### Returning distinct values
```sql
SELECT DISTINCT status FROM orders ORDER BY status;
```

### Serial / identity columns
Do not try to INSERT into SERIAL or IDENTITY columns — they are auto-generated.

## Do Not Use
- MySQL-specific syntax: LIMIT x, y (use LIMIT x OFFSET y in PostgreSQL)
- SQL Server syntax: TOP N (use LIMIT N)
- Double-quoted identifiers for values — double quotes are for column/table names; single quotes are for string values.
