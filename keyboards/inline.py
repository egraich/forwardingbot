from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def forwards_list_keyboard(
    forwards: list, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Build a keyboard with a 🗑 Delete button under each forward."""
    builder = InlineKeyboardBuilder()
    for fwd in forwards:
        builder.row(
            InlineKeyboardButton(
                text=i18n.my.delete.button(),
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
