# SKILL-21: Token Budget Awareness

## Why This Matters
You are a small model with a limited context window.
Every tool result consumes tokens. If tool results are too large, you will lose earlier context
and start making errors — wrong table names, forgotten filters, hallucinated values.

## Hard Budget Rules

| Content type              | Max tokens to consume |
|---------------------------|-----------------------|
| Schema inspection result  | ~300 tokens           |
| Single query result       | ~500 tokens           |
| Total tool results per turn | 1,000 tokens max    |
| Your own reasoning        | Keep short and direct |

## How to Stay Within Budget

### For query results
Never return more than 20 raw rows to yourself. Summarise anything larger.
20 rows × ~20 tokens per row = ~400 tokens. That is safe.

### For schema results
Only fetch the columns you need. Do not dump the entire information_schema.
Ask for one table at a time.

### For multi-step queries
Use CTEs so you do one round-trip to the DB, not many.

## Warning Signs You Are Over Budget
- You forget the table name you queried two steps ago.
- You repeat a query you already ran.
- You start mixing up column values between rows.
- You add a filter that was not in the user's question.

If any of these happen: stop, re-read the original user request, and start fresh with a single targeted query.

## Golden Rule
Less data, more precisely filtered = better answers from you.
More data, loosely filtered = hallucinations.
