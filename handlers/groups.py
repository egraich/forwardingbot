from aiogram import F, Router
from aiogram.types import Message
from asyncpg import Pool

from database.queries import get_active_targets

router = Router()


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: Message, db_pool: Pool):
    """Copy incoming group messages to active target chats."""
    targets = await get_active_targets(db_pool, message.chat.id)
    for target_id in targets:
        try:
            await message.send_copy(chat_id=target_id)
        except Exception:
            pass


@router.channel_post()
async def handle_channel_post(message: Message, db_pool: Pool):
    """Copy incoming channel posts to active target chats."""
    targets = await get_active_targets(db_pool, message.chat.id)
    for target_id in targets:
        try:
            await message.send_copy(chat_id=target_id)
        except Exception:
            pass