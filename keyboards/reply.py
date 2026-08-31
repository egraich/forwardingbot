from aiogram.types import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    ReplyKeyboardMarkup,
)
from fluentogram import TranslatorRunner


def get_source_keyboard(i18n: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Return a reply keyboard prompting the user to select a source group or channel."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.button.source.group(),
                    request_chat=KeyboardButtonRequestChat(
                        request_id=1, chat_is_channel=False
                    ),
                ),
                KeyboardButton(
                    text=i18n.button.source.channel(),
                    request_chat=KeyboardButtonRequestChat(
                        request_id=2, chat_is_channel=True
                    ),
                ),
            ]
        ],
        resize_keyboard=True,
    )


def get_target_keyboard(i18n: TranslatorRunner) -> ReplyKeyboardMarkup:
    """Return a reply keyboard prompting the user to select a target group or channel."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.button.target.group(),
                    request_chat=KeyboardButtonRequestChat(
                        request_id=3, chat_is_channel=False
                    ),
                ),
                KeyboardButton(
                    text=i18n.button.target.channel(),
                    request_chat=KeyboardButtonRequestChat(
                        request_id=4, chat_is_channel=True
                    ),
                ),
            ]
        ],
        resize_keyboard=True,
    )