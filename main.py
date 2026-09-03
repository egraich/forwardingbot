import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.types import (
    BotCommandScopeAllPrivateChats as ScopeAllPrivateChats,
)
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

import config
from database.connection import create_db_pool
from database.init_db import init_database
from handlers import groups, private
from middlewares.db import DbSessionMiddleware
from middlewares.i18n import i18nMiddleware


_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """Configure root logger: stdout + rotating file, formatted with bracketed timestamp."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_LOG_DATEFMT)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    try:
        file_handler = RotatingFileHandler(
            filename="bot.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError as exc:
        # If we can't write the log file (e.g. read-only FS), keep stdout only.
        logging.getLogger(__name__).warning(
            "could not open bot.log, file logging disabled: %s", exc
        )

    # aiogram is chatty on DEBUG, dial it down
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


def setup_i18n() -> TranslatorHub:
    """Configure fluentogram translator hub with supported locales."""
    return TranslatorHub(
        locales_map={"ru": ("ru", "en"), "en": ("en", "ru")},
        translators=[
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    "ru-RU", filenames=["locales/ru/texts.ftl"]
                ),
            ),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    "en-US", filenames=["locales/en/texts.ftl"]
                ),
            ),
        ],
        root_locale="en",
    )


async def main():
    """Initialize bot, database, middlewares, routers, and start polling."""
    setup_logging()
    log = logging.getLogger("bot.main")

    log.info("starting bot, pid=%d", __import__("os").getpid())
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    log.info("connecting to PostgreSQL at %s:%s", config.DB_HOST, config.DB_PORT)
    pool = await create_db_pool()
    log.info("running init_database")
    await init_database(pool)
    log.info("database ready")

    t_hub = setup_i18n()
    log.info("i18n hub ready (locales: ru, en)")

    dp.update.middleware(DbSessionMiddleware(pool))
    dp.update.middleware(i18nMiddleware(t_hub))

    dp.include_router(private.router)
    dp.include_router(groups.router)
    log.info("routers included: private, groups")

    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Создать пересылку / Create forward"),
            BotCommand(command="my", description="Мои пересылки / My forwards"),
        ],
        scope=ScopeAllPrivateChats(),
    )
    log.info("bot commands registered: /start, /my")

    bot_info = await bot.get_me()
    log.info(
        "polling started: bot_id=%s username=@%s",
        bot_info.id,
        bot_info.username,
    )

    try:
        await dp.start_polling(bot)
    finally:
        log.info("shutting down, closing db pool")
        await pool.close()
        log.info("shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())