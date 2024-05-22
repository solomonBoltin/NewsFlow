from dotenv import load_dotenv
import os

load_dotenv()

GENAI_KEY = os.getenv("GENAI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ARTICLE_PREVIEW_CHANNEL = os.getenv('TELEGRAM_ARTICLE_PREVIEW_CHANNEL')
