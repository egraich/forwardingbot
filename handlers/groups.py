import logging

from aiogram import F, Router
from aiogram.types import Message
from asyncpg import Pool

from database.queries import get_active_targets

router = Router()
log = logging.getLogger("bot.groups")


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: Message, db_pool: Pool):
    """Copy incoming group messages to active target chats."""
    source_id = message.chat.id
    targets = await get_active_targets(db_pool, source_id)
    if not targets:
        return
    log.info(
        "group msg source_chat=%s message_id=%s targets=%s",
        source_id,
        message.message_id,
        targets,
    )
    for target_id in targets:
        try:
            await message.send_copy(chat_id=target_id)
            log.debug(
                "forwarded source_chat=%s -> target_chat=%s message_id=%s",
                source_id,
                target_id,
                message.message_id,
            )
        except Exception as exc:
            log.exception(
                "forward failed source_chat=%s -> target_chat=%s message_id=%s: %s",
                source_id,
                target_id,
                message.message_id,
                exc,
            )


@router.channel_post()
async def handle_channel_post(message: Message, db_pool: Pool):
    """Copy incoming channel posts to active target chats."""
    source_id = message.chat.id
    targets = await get_active_targets(db_pool, source_id)
    if not targets:
        return
    log.info(
        "channel post source_chat=%s message_id=%s targets=%s",
        source_id,
        message.message_id,
        targets,
    )
    for target_id in targets:
        try:
            await message.send_copy(chat_id=target_id)
            log.debug(
                "forwarded source_chat=%s -> target_chat=%s message_id=%s",
                source_id,
                target_id,
                message.message_id,
            )
        except Exception as exc:
            log.exception(
                "forward failed source_chat=%s -> target_chat=%s message_id=%s: %s",
                source_id,
                target_id,
                message.message_id,
                exc,
            )
