# SKILL-12: SQL Error Handling and Recovery

## When
The database returns an error instead of rows.

## Step-by-Step Recovery

### Step 1 — Read the error message carefully
PostgreSQL errors contain: error type, the problematic token, and a hint.
Example: `ERROR: column "custmer_name" does not exist`

### Step 2 — Identify the error type

| Error message contains          | Likely cause              | Fix                                      |
|---------------------------------|---------------------------|------------------------------------------|
| column "x" does not exist       | Typo in column name       | Call get_schema(), use correct name      |
| relation "x" does not exist     | Typo in table name        | List tables, use correct name            |
| syntax error at or near "x"     | SQL syntax mistake        | Rewrite the query                        |
| operator does not exist         | Wrong type comparison     | Cast the value: col::text, col::integer  |
| division by zero                | Aggregation edge case     | Wrap divisor: NULLIF(divisor, 0)         |
| permission denied               | Access restricted         | Tell user, do not retry                  |

### Step 3 — Fix and retry once
Correct the query and execute once more.

### Step 4 — If still failing
Tell the user what you tried and what error remains. Do not loop more than 2 attempts.
Say: "I encountered an error querying that data: [error]. Please verify the table name or column with your database administrator."

## Do Not
- Silently ignore errors and return empty results.
- Retry the exact same failing query.
- Expose raw stack traces to the user — summarise the issue in plain language.
