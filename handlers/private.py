from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from asyncpg import Pool
from fluentogram import TranslatorRunner

router = Router()

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


def _chat_link(chat_id: int) -> str | None:
    """Build a deep-link to a chat. Returns None if a usable link cannot be built."""
    s = str(chat_id)
    if s.startswith("-100"):
        return f"https://t.me/c/{s[4:]}"
    return None


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


@router.message(Command("my"), F.chat.type == "private")
async def cmd_my(
    message: Message, db_pool: Pool, i18n: TranslatorRunner
):
    """Show the user their active forwards as a list with delete buttons."""
    forwards = await get_user_forwards(db_pool, message.from_user.id)

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
        src_link = _chat_link(src) or f"<code>{src}</code>"
        tgt_link = _chat_link(tgt) or f"<code>{tgt}</code>"
        lines.append(
            i18n.my.item(
                n=idx,
                source_link=src_link,
                target_link=tgt_link,
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
    owner_id = await get_forward_owner(db_pool, forward_id)

    if owner_id is None or owner_id != callback.from_user.id:
        await callback.answer(i18n.my.delete.not_owner(), show_alert=True)
        return

    forwards = await get_user_forwards(db_pool, callback.from_user.id)
    target_fwd = next((f for f in forwards if f["id"] == forward_id), None)
    if not target_fwd:
        await callback.answer(i18n.my.delete.not_found(), show_alert=True)
        return

    src = target_fwd["source_chat_id"]
    tgt = target_fwd["target_chat_id"]
    src_link = _chat_link(src) or f"<code>{src}</code>"
    tgt_link = _chat_link(tgt) or f"<code>{tgt}</code>"

    await callback.message.edit_text(
        i18n.my.delete.confirm_text(
            fwd_id=forward_id, source_link=src_link, target_link=tgt_link
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
    deleted = await delete_forward(
        db_pool, forward_id, callback.from_user.id
    )

    if deleted:
        await callback.message.edit_text(i18n.my.delete.success())
    else:
        await callback.message.edit_text(i18n.my.delete.not_found())
    await callback.answer()


@router.callback_query(F.data == "cancel_del")
async def on_delete_cancel(callback: CallbackQuery, i18n: TranslatorRunner):
    """Cancel a pending deletion and remove the prompt."""
    await callback.answer(i18n.my.delete.cancelled())
    await callback.message.delete()


@router.callback_query(F.data == "hint_start")
async def on_hint_start(callback: CallbackQuery, i18n: TranslatorRunner):
    """Hint the user to run /start manually (callback cannot trigger a command)."""
    await callback.answer(i18n.my.empty.hint(), show_alert=True)