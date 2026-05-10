# SKILL-18: Type Casting in PostgreSQL

## When
Comparing columns of different types, formatting output, or converting user input values.

## Rule
PostgreSQL is strict about types. Comparing an integer column to a string literal will error.
Always match the type of the value to the type of the column.

## Cast Syntax
Two ways to cast — prefer the :: shorthand:
```sql
-- Preferred
SELECT order_id::text, total::integer FROM orders;

-- Also valid
SELECT CAST(order_id AS text), CAST(total AS integer) FROM orders;
```

## Common Casts

| Need                           | Cast                              |
|--------------------------------|-----------------------------------|
| Number to text for display     | col::text                         |
| Text to integer for comparison | '42'::integer                     |
| Text to date                   | '2024-01-01'::date                |
| Timestamp to date only         | created_at::date                  |
| Float to 2 decimal places      | ROUND(col::numeric, 2)            |
| Boolean from integer           | (col = 1)::boolean                |

## Common Error and Fix
Error: `operator does not exist: integer = text`
Fix: Cast one side — `WHERE id = '42'::integer` or `WHERE id::text = '42'`

## User Input Safety
If a user provides a value like "2024-01-15", cast it explicitly:
```sql
WHERE created_at >= '2024-01-15'::date
```
This prevents ambiguous type inference.

## Do Not
Let PostgreSQL silently coerce types — explicit casts make the query predictable.
