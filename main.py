import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fluentogram import FluentTranslator, TranslatorHub
from fluentogram.ftl_cli import FluentBundle

import config
from database.connection import create_db_pool
from database.init_db import init_database
from handlers import groups, private
from middlewares.db import DbSessionMiddleware
from middlewares.i18n import i18nMiddleware


def setup_i18n() -> TranslatorHub:
    """Configure fluentogram translator hub with supported locales."""
    return TranslatorHub(
        locales_map={"ru": ("ru", "en"), "en": ("en", "ru")},
        translators=[
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    "ru", filenames=["locales/ru/texts.ftl"]
                ),
            ),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    "en", filenames=["locales/en/texts.ftl"]
                ),
            ),
        ],
        root_locale="en",
    )


async def main():
    """Initialize bot, database, middlewares, routers, and start polling."""
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    pool = await create_db_pool()
    await init_database(pool)

    t_hub = setup_i18n()

    dp.update.middleware(DbSessionMiddleware(pool))
    dp.update.middleware(i18nMiddleware(t_hub))

    dp.include_router(private.router)
    dp.include_router(groups.router)

    try:
        await dp.start_polling(bot)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())