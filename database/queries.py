from typing import List, Optional
import asyncpg


async def add_user_and_create_draft(
    pool: asyncpg.Pool, user_id: int, username: Optional[str]
) -> None:
    """Register a user and create a new forward draft, clearing existing unfinished drafts."""
    async with pool.acquire() as conn:
        async with conn.transaction():
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
                """,
                user_id,
            )
            await conn.execute(
                """
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


async def get_user_forwards(
    pool: asyncpg.Pool, user_id: int
) -> list[asyncpg.Record]:
    """Return all active forwards owned by a user."""
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT id, source_chat_id, target_chat_id, created_at
            FROM forwards
            WHERE owner_id = $1 AND status = 'active'
            ORDER BY created_at DESC;
            """,
            user_id,
        )


async def get_forward_owner(pool: asyncpg.Pool, forward_id: int) -> Optional[int]:
    """Check the owner of a forward (prevents deleting others' forwards)."""
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT owner_id FROM forwards WHERE id = $1;",
            forward_id,
        )


async def delete_forward(
    pool: asyncpg.Pool, forward_id: int, owner_id: int
) -> bool:
    """Delete a forward only if the owner matches. Returns True if deleted."""
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM forwards WHERE id = $1 AND owner_id = $2;",
            forward_id,
            owner_id,
        )
        # asyncpg returns 'DELETE N', e.g. 'DELETE 1'
        return result == "DELETE 1"