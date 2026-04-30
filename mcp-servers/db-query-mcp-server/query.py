import re
from typing import Any, List, Tuple

_VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def _validate_identifier(value: str, field_name: str):
    if not _VALID_IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {field_name}: {value}")


def build_select_query(
    table: str,
    projection: List[str],
    where: dict[str, Any] | None = None,
    joins: List[str] | None = None,
    group_by: List[str] | None = None,
    having: str | None = None,
    order_by: List[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> Tuple[str, List[Any]]:

    # Validate table
    _validate_identifier(table, "table")

    # Validate projection
    if not projection:
        raise ValueError("projection cannot be empty")

    for col in projection:
        if col != "*" and " " not in col:  # allow "COUNT(*) as c"
            _validate_identifier(col, "projection column")

    sql = f"SELECT {', '.join(projection)} FROM {table}"

    # Joins (controlled but still flexible)
    if joins:
        for j in joins:
            if not j.upper().startswith(("JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN")):
                raise ValueError(f"Invalid join clause: {j}")
        sql += " " + " ".join(joins)

    params: List[Any] = []

    # WHERE (SAFE)
    if where:
        conditions = []
        for col, val in where.items():
            _validate_identifier(col, "where column")

            if val is None:
                conditions.append(f"{col} IS NULL")
            elif isinstance(val, list):
                placeholders = ", ".join(["?"] * len(val))
                conditions.append(f"{col} IN ({placeholders})")
                params.extend(val)
            else:
                conditions.append(f"{col} = ?")
                params.append(val)

        sql += " WHERE " + " AND ".join(conditions)

    # GROUP BY
    if group_by:
        for col in group_by:
            _validate_identifier(col, "group_by column")
        sql += " GROUP BY " + ", ".join(group_by)

    # HAVING (restricted)
    if having:
        if not group_by:
            raise ValueError("HAVING requires GROUP BY")
        sql += f" HAVING {having}"

    # ORDER BY
    if order_by:
        for col in order_by:
            if not re.fullmatch(r"[A-Za-z0-9_.]+\s+(ASC|DESC)", col, re.IGNORECASE):
                raise ValueError(f"Invalid order_by: {col}")
        sql += " ORDER BY " + ", ".join(order_by)

    if limit is not None:
        if limit < 0 or limit > 100:
            raise ValueError("limit must be between 0 and 100")
        sql += f" LIMIT {limit}"

    if offset is not None:
        if offset < 0:
            raise ValueError("offset must be >= 0")
        sql += f" OFFSET {offset}"

    return sql, params

import asyncpg
import re


def _convert_placeholders(sql: str) -> str:
    counter = 0

    def repl(_):
        nonlocal counter
        counter += 1
        return f"${counter}"

    return re.sub(r"\?", repl, sql)


async def execute_query(dsn: str, sql: str, params: list):
    pg_sql = _convert_placeholders(sql)

    conn = await asyncpg.connect(dsn)
    try:
        rows = await conn.fetch(pg_sql, *params, timeout=5)
        return [dict(r) for r in rows]
    finally:
        await conn.close()