# SKILL-11: Summarise Results Before Responding

## When
Any time a query returns more than 20 rows, or the raw result is a long list of numbers.

## Rule
Do not dump raw rows at the user. Transform results into a readable human response.

## How to Summarise

### Small result (≤ 20 rows)
Present as a clean table or short list. Include column headers.

### Medium result (21–200 rows)
Show:
- Total count
- Top 5–10 rows (most relevant)
- A note: "Showing 10 of 87 results. Ask me to filter further."

### Large result (> 200 rows — should not happen if other skills followed)
Show only aggregated statistics. Never show raw rows.

## Example Response Pattern

Bad:
> (12,345 rows of JSON dumped to user)

Good:
> Found 87 pending orders totalling $14,230. Here are the 10 most recent:
> | order_id | customer  | total  | date       |
> |----------|-----------|--------|------------|
> | 1042     | Alice M.  | $320   | 2024-11-10 |
> ...
> Ask me to filter by customer, date range, or status.

## Monetary Values
Always format with currency symbol and 2 decimal places: $1,234.56

## Dates
Always display in a readable format: Nov 10, 2024 or 2024-11-10. Never raw timestamps.
