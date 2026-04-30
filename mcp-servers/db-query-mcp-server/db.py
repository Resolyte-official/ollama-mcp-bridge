import asyncpg
from dataclasses import dataclass


@dataclass
class DbConfig:
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_sslmode: str


def new_db_config() -> DbConfig:
    return DbConfig(
        db_user="mcpserver",
        db_password="open-db",
        db_host="db",
        db_port=5432,
        db_name="school-db",
        db_sslmode="disable",
    )


async def new_db_pool(config: DbConfig):
    dsn = f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"

    pool = await asyncpg.create_pool(dsn=dsn)

    # ping check (similar to Go)
    async with pool.acquire() as conn:
        try:
            await conn.execute("SELECT 1")
        except Exception:
            raise RuntimeError("unable to ping db")

    return pool