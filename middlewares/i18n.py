from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub


class i18nMiddleware(BaseMiddleware):
    """Middleware for injecting fluentogram translator runner into event data based on user locale."""

    def __init__(self, t_hub: TranslatorHub):
        super().__init__()
        self.t_hub = t_hub

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        language = user.language_code if user else "en"
        if language not in ("ru", "en"):
            language = "en"

        data["i18n"] = self.t_hub.get_translator_by_locale(language)
        return await handler(event, data)