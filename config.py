import os
from dotenv import load_dotenv

# load_dotenv() # <--- Agar .env dan o'qish kerak bo'lsa yoqilgan bo'ladi,
                 #      lekin Vercel'da o'chirilgan bo'lishi kerak.

# Maxfiy kalitlar (Vercel Environment Variables orqali o'qiladi)
BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")
VERCEL_URL = os.getenv("VERCEL_URL") # Vercel o'zi beradi

# Bot konfiguratsiyasi
CONTACT_INFO = {
    'telegram_accounts': ['@GOKOREABOT_ADMIN', '@gokorea_ceo'],
    'phone': '+82 10-xxxx-xxxx',
    'channel': '@gokorea_official'
}
IMAGE_DIR = 'images'
USER_DATA_FILE = 'users_data.json'
REFERRAL_DATA_FILE = 'referral_data.json'
REFERRAL_BONUS = {
    'registration': 50000, # So'm
    'commission': 0.05     # Foiz
}

# Webhook konfiguratsiyasi (app.py uchun kerak)
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{VERCEL_URL}{WEBHOOK_PATH}" if VERCEL_URL else None