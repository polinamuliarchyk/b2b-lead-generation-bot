import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
MANAGERS_CHAT_ID = os.getenv("MANAGERS_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("Error: Токен бота не найден!")