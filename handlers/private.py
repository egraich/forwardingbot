import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from asyncpg import Pool
from fluentogram import TranslatorRunner

router = Router()
log = logging.getLogger("bot.private")

from database.queries import (
    add_user_and_create_draft,
    delete_forward,
    get_forward_owner,
    get_user_forwards,
    set_source_chat,
    set_target_chat,
)
from keyboards.inline import (
    confirm_delete_keyboard,
    empty_state_keyboard,
    forwards_list_keyboard,
)
from keyboards.reply import get_source_keyboard, get_target_keyboard


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Handle /start command in private chat and initiate setup flow."""
    user = message.from_user
    log.info(
        "cmd_start user_id=%s username=%s",
        user.id if user else None,
        user.username if user else None,
    )
    await add_user_and_create_draft(
        db_pool, user.id, user.username
    )
    await message.answer(
        i18n.start.welcome(name=user.first_name),
        reply_markup=get_source_keyboard(i18n),
    )


@router.message(F.chat_shared, F.chat.type == "private")
async def handle_chat_shared(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Handle chat selection event from native request_chat buttons."""
    chat_id = message.chat_shared.chat_id
    user_id = message.from_user.id
    log.info(
        "chat_shared user_id=%s chat_id=%s", user_id, chat_id
    )

    is_source_set = await set_source_chat(db_pool, user_id, chat_id)
    if is_source_set:
        log.info(
            "source set user_id=%s chat_id=%s", user_id, chat_id
        )
        await message.answer(
            i18n.source.success(),
            reply_markup=get_target_keyboard(i18n),
        )
        return

    is_target_set = await set_target_chat(db_pool, user_id, chat_id)
    if is_target_set:
        log.info(
            "target set user_id=%s chat_id=%s -> forward active",
            user_id,
            chat_id,
        )
        await message.answer(
            i18n.setup.complete(), reply_markup=ReplyKeyboardRemove()
        )
    else:
        log.warning(
            "chat_shared could not match source or target user_id=%s chat_id=%s",
            user_id,
            chat_id,
        )


@router.message(Command("my"), F.chat.type == "private")
async def cmd_my(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Show the user their active forwards as a list with delete buttons."""
    user_id = message.from_user.id
    log.info("cmd_my user_id=%s", user_id)
    forwards = await get_user_forwards(db_pool, user_id)
    log.info(
        "cmd_my user_id=%s forwards_count=%s", user_id, len(forwards)
    )

    if not forwards:
        await message.answer(
            i18n.my.empty.text(),
            reply_markup=empty_state_keyboard(i18n),
        )
        return

    lines = [i18n.my.header(count=len(forwards)), ""]
    for idx, fwd in enumerate(forwards, start=1):
        src = fwd["source_chat_id"]
        tgt = fwd["target_chat_id"]
        lines.append(
            i18n.my.item(
                n=idx,
                source_id=src,
                target_id=tgt,
                fwd_id=fwd["id"],
            )
        )

    await message.answer(
        "\n".join(lines),
        reply_markup=forwards_list_keyboard(forwards, i18n),
    )


@router.callback_query(F.data.startswith("del:"))
async def on_delete_request(
    callback: CallbackQuery, db_pool: Pool, i18n: TranslatorRunner
):
    """Show the delete confirmation prompt for the chosen forward."""
    forward_id = int(callback.data.split(":", 1)[1])
    user_id = callback.from_user.id
    log.info(
        "del request user_id=%s forward_id=%s", user_id, forward_id
    )
    owner_id = await get_forward_owner(db_pool, forward_id)

    if owner_id is None or owner_id != user_id:
        log.warning(
            "del rejected (not owner) user_id=%s forward_id=%s owner_id=%s",
            user_id,
            forward_id,
            owner_id,
        )
        await callback.answer(i18n.my.delete.not_owner(), show_alert=True)
        return

    forwards = await get_user_forwards(db_pool, user_id)
    target_fwd = next((f for f in forwards if f["id"] == forward_id), None)
    if not target_fwd:
        log.warning(
            "del rejected (not found) user_id=%s forward_id=%s",
            user_id,
            forward_id,
        )
        await callback.answer(i18n.my.delete.not_found(), show_alert=True)
        return

    await callback.message.edit_text(
        i18n.my.delete.confirm_text(
            fwd_id=forward_id,
            source_id=target_fwd["source_chat_id"],
            target_id=target_fwd["target_chat_id"],
        ),
        reply_markup=confirm_delete_keyboard(forward_id, i18n),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_del:"))
async def on_delete_confirm(
    callback: CallbackQuery, db_pool: Pool, i18n: TranslatorRunner
):
    """Confirm deletion of a forward."""
    forward_id = int(callback.data.split(":", 1)[1])
    user_id = callback.from_user.id
    log.info(
        "confirm_del user_id=%s forward_id=%s", user_id, forward_id
    )
    deleted = await delete_forward(db_pool, forward_id, user_id)

    if deleted:
        log.info(
            "forward deleted user_id=%s forward_id=%s",
            user_id,
            forward_id,
        )
        await callback.message.edit_text(i18n.my.delete.success())
    else:
        log.warning(
            "confirm_del failed (row missing) user_id=%s forward_id=%s",
            user_id,
            forward_id,
        )
        await callback.message.edit_text(i18n.my.delete.not_found())
    await callback.answer()


@router.callback_query(F.data == "cancel_del")
async def on_delete_cancel(callback: CallbackQuery, i18n: TranslatorRunner):
    """Cancel a pending deletion and remove the prompt."""
    log.info("cancel_del user_id=%s", callback.from_user.id)
    await callback.answer(i18n.my.delete.cancelled())
    await callback.message.delete()


@router.callback_query(F.data == "hint_start")
async def on_hint_start(callback: CallbackQuery, i18n: TranslatorRunner):
    """Hint the user to run /start manually (callback cannot trigger a command)."""
    log.info("hint_start user_id=%s", callback.from_user.id)
    await callback.answer(i18n.my.empty.hint(), show_alert=True)