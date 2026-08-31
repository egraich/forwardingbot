# Telegram Forwarding Bot

A multi-user, asynchronous Telegram bot designed to forward messages between groups and channels without cluttering target chats or requiring manual ID copying. Built with `aiogram 3.x`, `asyncpg`, `fluentogram`, and PostgreSQL.

## Features

- **Multi-Tenant Routing:** Users can configure multiple individual forward routes (Source $\rightarrow$ Target).
- **Native UX (No Group Spam):** Uses Telegram's native `KeyboardButtonRequestChat` interface to select groups and channels directly from private messages.
- **Privacy First:** Eliminates the need to paste group IDs or run setup commands inside public or private chats.
- **High Performance:** Raw SQL via `asyncpg` with partial indexes optimized for zero-latency forwarding checks.
- **Internationalization (i18n):** Native support for English and Russian via `fluentogram` (Project Fluent), automatically selected based on the user's Telegram locale.
- **Stateless Setup:** Route setup state is stored directly in PostgreSQL, eliminating Redis dependencies.

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** `aiogram 3.x`
- **Database:** PostgreSQL 16
- **Database Driver:** `asyncpg` (Raw SQL)
- **i18n Engine:** `fluentogram` (Mozilla Fluent)
- **Containerization:** Docker & Docker Compose

---

## Project Structure

```text
.
├── .env.example            # Environment variables template
├── docker-compose.yml      # PostgreSQL container configuration
├── Dockerfile              # Bot application containerization
├── main.py                 # Application entry point
├── config.py               # Environment configuration loader
├── database/
│   ├── connection.py       # asyncpg connection pool initialization
│   ├── init_db.py          # Database schema and index creation
│   └── queries.py          # Async SQL queries
├── handlers/
│   ├── private.py          # Private chat handlers (/start, chat setup)
│   └── groups.py           # Message forwarding logic (groups & channels)
├── keyboards/
│   └── reply.py            # Reply keyboards with native chat request buttons
├── locales/
│   ├── en/texts.ftl        # Fluent localization (English)
│   └── ru/texts.ftl        # Fluent localization (Russian)
└── middlewares/
    ├── db.py               # Database pool injection middleware
    └── i18n.py             # User locale detection middleware