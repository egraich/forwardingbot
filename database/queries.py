import asyncpg
from typing import Optional, List

async def add_user_and_create_draft(pool: asyncpg.Pool, user_id: int, username: Optional[str]):
    """Регистрирует юзера и создает/обновляет для него черновик связки"""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username) 
            VALUES ($1, $2) 
            ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username;
            """,
            user_id, username
        )
        
        # Если у юзера уже есть висящий черновик — сбрасываем его на шаг waiting_source.
        # Если черновика нет — создаем новый.
        await conn.execute(
            """
            DELETE FROM forwards 
            WHERE owner_id = $1 AND status IN ('waiting_source', 'waiting_target');
            
            INSERT INTO forwards (owner_id, status) VALUES ($1, 'waiting_source');
            """,
            user_id
        )

async def set_source_chat(pool: asyncpg.Pool, user_id: int, chat_id: int) -> bool:
    """Записывает Source чат в черновик юзера"""
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            UPDATE forwards 
            SET source_chat_id = $1, status = 'waiting_target'
            WHERE owner_id = $2 AND status = 'waiting_source'
            RETURNING id;
            """,
            chat_id, user_id
        )
        return bool(result)

async def set_target_chat(pool: asyncpg.Pool, user_id: int, chat_id: int) -> bool:
    """Записывает Target чат и активирует связку"""
    async with pool.acquire() as conn:
        try:
            result = await conn.fetchval(
                """
                UPDATE forwards 
                SET target_chat_id = $1, status = 'active'
                WHERE owner_id = $2 AND status = 'waiting_target'
                RETURNING id;
                """,
                chat_id, user_id
            )
            return bool(result)
        except asyncpg.UniqueViolationError:
            # Сработает, если точно такая же связка уже есть у кого-то
            return False

async def get_active_targets(pool: asyncpg.Pool, source_chat_id: int) -> List[int]:
    """Быстрый запрос: находит все target_chat_id для входящего сообщения"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT target_chat_id 
            FROM forwards 
            WHERE source_chat_id = $1 AND status = 'active';
            """,
            source_chat_id
        )
        return [r['target_chat_id'] for r in rows if r['target_chat_id'] is not None]