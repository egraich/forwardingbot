import asyncpg

INIT_SQL = """
DO $$ BEGIN
    CREATE TYPE forward_status AS ENUM (
        'waiting_source', 
        'waiting_target', 
        'active'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS forwards (
    id SERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    source_chat_id BIGINT,
    target_chat_id BIGINT,
    status forward_status DEFAULT 'waiting_source',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_forward_route UNIQUE NULLS NOT DISTINCT (source_chat_id, target_chat_id)
);

CREATE INDEX IF NOT EXISTS idx_active_sources 
ON forwards(source_chat_id) 
WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_user_drafts 
ON forwards(owner_id) 
WHERE status IN ('waiting_source', 'waiting_target');
"""


async def init_database(pool: asyncpg.Pool) -> None:
    """Initialize database schemas, custom types, tables, and indexes."""
    async with pool.acquire() as conn:
        await conn.execute(INIT_SQL)