# Knowledge Skills - Controls how the agent thinks

These skills are instructions, information to help agent for
approaching towards tasks.

Tool/Pipeline skills are out of scope for now these provides 
ability to invoke execution based on the provided Interface Specs.

Lastly, In real, skill can combine all the above types of skills.

## Skills Indexes 

**Query Safety (protect the DB and the context window)**
- [SKILL-01](../mcp-skills/skill_01_explicit_columns.md) — Explicit columns, never SELECT *
- [SKILL-02](../mcp-skills/skill_02_always_limit.md) — Always add LIMIT
- [SKILL-03](../mcp-skills/skill_03_count_before_fetch.md) — COUNT before fetch
- [SKILL-04](../mcp-skills/skill_04_read_only.md) — Read-only enforcement (no INSERT/UPDATE/DELETE ever)
- [SKILL-17](../mcp-skills/skill_17_explain_check.md) — EXPLAIN before running on large tables

**Schema & Structure**
- [SKILL-05](../mcp-skills/skill_05_schema_inspection.md) — Inspect schema before querying unknown tables
- [SKILL-09](../mcp-skills/skill_09_join_construction.md) — JOIN construction rules with aliases
- [SKILL-15](../mcp-skills/skill_15_cte_usage.md) — Use CTEs to break complex queries into steps
- [SKILL-20](../mcp-skills/skill_20_avoid_n_plus_1.md) — Avoid the N+1 query pattern

**Data Correctness**
- [SKILL-06](../mcp-skills/skill_06_null_handling.md) — NULL handling (IS NULL, COALESCE, NULLS LAST)
- [SKILL-07](../mcp-skills/skill_07_datetime_queries.md) — Date/time queries in PostgreSQL
- [SKILL-08](../mcp-skills/skill_08_text_search.md) — Text search with ILIKE vs full-text
- [SKILL-10](../mcp-skills/skill_10_aggregation.md) — Aggregation with GROUP BY and HAVING
- [SKILL-16](../mcp-skills/skill_16_window_functions.md) — Window functions for rankings and running totals
- [SKILL-18](../mcp-skills/skill_18) — Type casting to prevent type mismatch errors
- [SKILL-22](../mcp-skills/skill_22_postgres_syntax.md) — PostgreSQL-specific syntax (not MySQL, not SQL Server)
- [SKILL-23](../mcp-skills/skill_23_safe_values.md) — Handling user-provided values safely

**Result Management (directly addresses the hallucination problem)**
- [SKILL-11](../mcp-skills/skill_11_result_summarisation.md) — Summarise results before responding
- [SKILL-13 ](../mcp-skills/skill_13_pagination.md) — Pagination with OFFSET vs keyset
- [SKILL-21](../mcp-skills/skill_21_token_budget.md) — Token budget awareness — the small model's self-awareness skill

**Agent Behaviour**
- [SKILL-12](../mcp-skills/skill_12_error_handling.md) — SQL error handling and recovery
- [SKILL-14](../mcp-skills/skill_14_disambiguation.md) — Disambiguating vague user requests
- [SKILL-19](../mcp-skills/skill_19_response_structure.md) — Structuring the final response to the user
- [SKILL-24](../mcp-skills/skill_24_avoid_n_plus_1.md) — Plan before you query (3-step internal plan)