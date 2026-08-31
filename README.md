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
```

Database Architecture

The application uses two tables, one custom ENUM type, and two partial indexes
to ensure low lookup overhead during message events.

Types & Tables

CREATE TYPE forward_status AS ENUM ('waiting_source', 'waiting_target', 'active');

CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE forwards (
    id SERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    source_chat_id BIGINT,
    target_chat_id BIGINT,
    status forward_status DEFAULT 'waiting_source',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_forward_route UNIQUE NULLS NOT DISTINCT (source_chat_id, target_chat_id)
);

Indexes

-- Partial index for active message routing
CREATE INDEX idx_active_sources 
ON forwards(source_chat_id) 
WHERE status = 'active';

-- Partial index for active setup drafts
CREATE INDEX idx_user_drafts 
ON forwards(owner_id) 
WHERE status IN ('waiting_source', 'waiting_target');

Environment Variables

Create a .env file in the root directory based on .env.example:

BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
DB_USER=egraich
DB_PASS=228_egor_228
DB_NAME=forwarding_bot
DB_HOST=nest_postgres_container
DB_PORT=5432

Deployment

Prerequisites

  - Docker and Docker Compose installed.
  - Bot token generated via @BotFather.
  - Disabled Group Privacy Mode in @BotFather (Bot Settings \rightarrow Group
    Privacy \rightarrow Turn OFF) to allow the bot to read messages in source
    groups.

Running via Docker Compose

1.  Clone the repository:

    git clone https://github.com/your-username/telegram-forwarding-bot.git
    cd telegram-forwarding-bot

2.  Copy .env.example to .env and fill in your credentials:

    cp .env.example .env

3.  Start the containers:

    docker-compose up -d --build

4.  Inspect logs:

    docker-compose logs -f

User Setup Workflow

1.  Send /start to the bot in private messages.
2.  Click "Select Source Group/Channel" to pick the chat you want to forward
    messages from.
3.  Click "Select Target Group/Channel" to pick the destination chat.
4.  Messages posted to the source chat will automatically copy to the target
    chat.

License

Distributed under the MIT License. See LICENSE for more information.

