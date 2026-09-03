import logging

import asyncpg
import config

log = logging.getLogger("bot.db.pool")


async def create_db_pool() -> asyncpg.Pool:
    """Create and return an asyncpg database connection pool."""
    log.info(
        "connecting: host=%s port=%s db=%s user=%s",
        config.DB_HOST,
        config.DB_PORT,
        config.DB_NAME,
        config.DB_USER,
    )
    pool = await asyncpg.create_pool(
        user=config.DB_USER,
        password=config.DB_PASS,
        database=config.DB_NAME,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )
    log.info("db pool established (min=1, max=%s)", pool.get_max_size())
    return pool
