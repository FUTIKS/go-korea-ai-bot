"""
Kanal ID ni aniqlash uchun yordamchi skript
"""
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def get_channel_info():
    bot = Bot(token=TOKEN)
    
    # Kanal username (@ bilan yoki @ siz)
    channel_username = "@GoKoreaGroup"  # O'zingizni kiriting
    
    try:
        chat = await bot.get_chat(channel_username)
        print("="*50)
        print(f"✅ Kanal topildi!")
        print(f"📝 Nomi: {chat.title}")
        print(f"🆔 ID: {chat.id}")
        print(f"👥 A'zolar: {chat.member_count if hasattr(chat, 'member_count') else 'Noma\'lum'}")
        print(f"📍 Username: @{chat.username}")
        print("="*50)
        print(f"\n📋 config.py ga qo'yish uchun:")
        print(f'REQUIRED_CHANNEL_ID = {chat.id}')
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        print("\n🔧 Tekshiring:")
        print("1. Bot kanalga admin qilinganmi?")
        print("2. Kanal username to'g'rimi?")
        print("3. Bot TOKEN to'g'rimi?")

if __name__ == "__main__":
    asyncio.run(get_channel_info())