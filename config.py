import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки PostgreSQL
DB_USER = os.getenv("DB_USER", "egraich")
DB_PASS = os.getenv("DB_PASS", "228_egor_228")
DB_NAME = os.getenv("DB_NAME", "forwarding_bot")
DB_HOST = os.getenv("DB_HOST", "nest_postgres_container")
DB_PORT = int(os.getenv("DB_PORT", 5432))