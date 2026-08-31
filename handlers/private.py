from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from asyncpg import Pool
from fluentogram import TranslatorRunner

router = Router()

from database.queries import (
    add_user_and_create_draft,
    set_source_chat,
    set_target_chat,
)
from keyboards.reply import get_source_keyboard, get_target_keyboard


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Handle /start command in private chat and initiate setup flow."""
    await add_user_and_create_draft(
        db_pool, message.from_user.id, message.from_user.username
    )
    await message.answer(
        i18n.start.welcome(name=message.from_user.first_name),
        reply_markup=get_source_keyboard(i18n),
    )


@router.message(F.chat_shared, F.chat.type == "private")
async def handle_chat_shared(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Handle chat selection event from native request_chat buttons."""
    chat_id = message.chat_shared.chat_id

    is_source_set = await set_source_chat(
        db_pool, message.from_user.id, chat_id
    )
    if is_source_set:
        await message.answer(
            i18n.source.success(),
            reply_markup=get_target_keyboard(i18n),
        )
        return

    is_target_set = await set_target_chat(
        db_pool, message.from_user.id, chat_id
    )
    if is_target_set:
        await message.answer(
            i18n.setup.complete(), reply_markup=ReplyKeyboardRemove()
        )