import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN topilmadi! .env faylni tekshiring.")

# Majburiy Kanal
REQUIRED_CHANNEL = "@GoKoreaGroup"
REQUIRED_CHANNEL_ID = -1002286453297  # Kanal ID (botni kanalga admin qiling!)

# Aloqa Ma'lumotlari
CONTACT_INFO = {
    "telegram_accounts": [
        "@gokorea_tashkent",
        "@gokorea_admin2", 
        "@gokorea_shahriyor"
    ],
    "phone": "+998 97 948 15 15",
    "channel": "https://t.me/GoKoreaGroup"
}

# Referal Tizimi
REFERRAL_BONUS = {
    "registration": 100,  # Ro'yxatdan o'tsa ($)
    "confirmed": 200      # Koreaga ketsa ($)
}

# Rasmlar papkasi
IMAGE_DIR = 'images'

# Til Kodlari
LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "uzb": "🇺🇿 Ўзбекча", 
    "en": "🇬🇧 English",
    "ko": "🇰🇷 한국어"
}

# Database fayl (JSON)
USER_DATA_FILE = "users_data.json"
REFERRAL_DATA_FILE = "referral_data.json"