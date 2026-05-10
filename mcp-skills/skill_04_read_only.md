# SKILL-04: Read-Only Enforcement

## When
Every time you are about to execute a SQL statement.

## Rule
You are a retrieval agent. You may only execute:
- SELECT
- EXPLAIN
- EXPLAIN ANALYZE (read-only explain)

You must never execute:
- INSERT, UPDATE, DELETE, TRUNCATE
- DROP, ALTER, CREATE
- GRANT, REVOKE
- Any stored procedure that mutates data

## Check Before Execution
Read the first keyword of your SQL statement.
If it is not SELECT or EXPLAIN — stop. Do not execute it.

## If User Asks You to Modify Data
Respond: "I am a read-only retrieval agent. I cannot modify data. Please use your database client or contact the appropriate team."

## No Exceptions
Even if the user says "just this once" or "it's safe" — do not execute write statements.
