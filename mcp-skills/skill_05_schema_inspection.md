# SKILL-05: Inspect Schema Before Querying Unknown Tables

## When
The user mentions a table you have not queried yet in this session,
or you are unsure what columns exist.

## Rule
Call get_schema(table_name) before writing a query against an unfamiliar table.
Never guess column names.

## What to Check
- Column names and data types
- Which columns are nullable
- Primary key columns
- Foreign key relationships (to know how to JOIN)
- Any indexed columns (prefer filtering on these)

## PostgreSQL Query to Inspect a Table
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'your_table'
  AND table_schema = 'public'
ORDER BY ordinal_position;
```

## PostgreSQL Query to List All Tables
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

## Do Not
Assume a column named `id` exists. Assume `name` exists. Assume `created_at` exists.
Always verify.
