from typing import List, Optional
import asyncpg


async def add_user_and_create_draft(
    pool: asyncpg.Pool, user_id: int, username: Optional[str]
) -> None:
    """Register a user and create a new forward draft, clearing existing unfinished drafts."""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username) 
            VALUES ($1, $2) 
            ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username;
            """,
            user_id,
            username,
        )
        await conn.execute(
            """
            DELETE FROM forwards 
            WHERE owner_id = $1 AND status IN ('waiting_source', 'waiting_target');
            
            INSERT INTO forwards (owner_id, status) VALUES ($1, 'waiting_source');
            """,
            user_id,
        )


async def set_source_chat(
    pool: asyncpg.Pool, user_id: int, chat_id: int
) -> bool:
    """Set the source chat ID for a user's pending forward draft."""
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            UPDATE forwards 
            SET source_chat_id = $1, status = 'waiting_target'
            WHERE owner_id = $2 AND status = 'waiting_source'
            RETURNING id;
            """,
            chat_id,
            user_id,
        )
        return bool(result)


async def set_target_chat(
    pool: asyncpg.Pool, user_id: int, chat_id: int
) -> bool:
    """Set the target chat ID for a user's pending forward draft and activate it."""
    async with pool.acquire() as conn:
        try:
            result = await conn.fetchval(
                """
                UPDATE forwards 
                SET target_chat_id = $1, status = 'active'
                WHERE owner_id = $2 AND status = 'waiting_target'
                RETURNING id;
                """,
                chat_id,
                user_id,
            )
            return bool(result)
        except asyncpg.UniqueViolationError:
            return False


async def get_active_targets(
    pool: asyncpg.Pool, source_chat_id: int
) -> List[int]:
    """Retrieve all active target chat IDs registered for a given source chat ID."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT target_chat_id 
            FROM forwards 
            WHERE source_chat_id = $1 AND status = 'active';
            """,
            source_chat_id,
        )
        return [
            r["target_chat_id"]
            for r in rows
            if r["target_chat_id"] is not None
        ]