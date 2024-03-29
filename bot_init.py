import telebot
from dotenv import load_dotenv

import os

load_dotenv(".env.dev")
apiKey = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(apiKey, skip_pending=True)
