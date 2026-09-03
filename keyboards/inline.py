from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def _short_id(chat_id: int) -> str:
    """Compact chat id representation suitable for button labels."""
    return str(chat_id)


def forwards_list_keyboard(
    forwards: list, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Build a keyboard with a 🗑 Delete button under each forward.

    Each button's label shows the source -> target pair so the user
    can identify which forward is being deleted.
    """
    builder = InlineKeyboardBuilder()
    for fwd in forwards:
        src = _short_id(fwd["source_chat_id"])
        tgt = _short_id(fwd["target_chat_id"])
        label = (
            f"{i18n.my.delete.button()}  {src} → {tgt}  #{fwd['id']}"
        )
        # Telegram limit on callback_data is 64 bytes.
        # 'del:<int>' always fits; int max is ~1e9 (10 chars), well under 64.
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"del:{fwd['id']}",
            )
        )
    return builder.as_markup()


def confirm_delete_keyboard(
    forward_id: int, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Build a confirmation keyboard: ✅ Yes / ❌ Cancel."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=i18n.my.delete.confirm(),
            callback_data=f"confirm_del:{forward_id}",
        ),
        InlineKeyboardButton(
            text=i18n.my.delete.cancel(),
            callback_data="cancel_del",
        ),
    )
    return builder.as_markup()


def empty_state_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Build a hint keyboard for the empty state."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.my.empty.button(),
                    callback_data="hint_start",
                )
            ]
        ]
    )
