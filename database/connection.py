import asyncpg
import config


async def create_db_pool() -> asyncpg.Pool:
    """Create and return an asyncpg database connection pool."""
    return await asyncpg.create_pool(
        user=config.DB_USER,
        password=config.DB_PASS,
        database=config.DB_NAME,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )