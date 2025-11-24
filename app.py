# app.py

import logging
import json
import os
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# !!!!!! MUHIM: Sizning bot.py dan quyidagi importlar o'zgarishsiz olinadi
from config import BOT_TOKEN, REQUIRED_CHANNEL, CONTACT_INFO, IMAGE_DIR, USER_DATA_FILE, REFERRAL_DATA_FILE, REFERRAL_BONUS, WEBHOOK_PATH, WEBHOOK_URL
from database.universities_data import UNIVERSITIES
from languages import uz_latin, uz_cyrillic, english, korean
from utils.helpers import is_subscribed_to_channel, generate_referral_code, format_contact_info

# ... (Sizning oldingi bot.py dagi barcha funksiyalar, masalan: 
#      load_user_data, save_user_data, get_user_language, get_text, 
#      delete_previous_message, send_message_smart, get_language_keyboard, 
#      get_main_keyboard, get_university_keyboard, get_university_detail_keyboard, 
#      get_back_keyboard, check_subscription, start, button_handler, send_main_menu
#      ni bu yerga to'liq ko'chirishingiz KERAK!)

# Agar sizning bot.py kodingizda funksiyalar to'liq joylashgan bo'lsa, 
# faqat quyidagi qismlarni o'zgartiramiz:

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask ilovasini yaratish
app = Flask(__name__)

# Bot Application'ni yaratish (Global darajada)
application = Application.builder().token(BOT_TOKEN).build()

# Oldingi bot.py dagi handlerlarni application'ga qo'shish
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# Webhook'dan kelgan so'rovlarni qabul qilish
@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_handler():
    """Telegramdan kelgan yangilanishlarni qabul qilish va ularga ishlov berish."""
    if request.method == "POST":
        # So'rovdagi JSON ma'lumotni olish
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Bot Application'ga yuborish
        await application.process_update(update)
        
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 405

@app.route('/', methods=['GET'])
def index():
    """Vercel'da ishlayotganini tekshirish uchun."""
    return 'Go Korea AI Bot is running on Webhook mode!'

async def setup_webhook():
    """Bot ishga tushirilganda Webhook'ni o'rnatish."""
    if WEBHOOK_URL:
        # Eski webhook'ni o'chirish
        await application.bot.delete_webhook()
        
        # Yangi webhook'ni o'rnatish
        is_set = await application.bot.set_webhook(url=WEBHOOK_URL)
        if is_set:
            logger.info(f"✅ Webhook muvaffaqiyatli o'rnatildi: {WEBHOOK_URL}")
        else:
            logger.error("❌ Webhook o'rnatishda xatolik yuz berdi!")
    else:
        logger.warning("VERCEL_URL topilmadi. Webhook o'rnatilmadi.")


# Barcha ma'lumotlarni yuklash (bot.py dagi kabi)
load_user_data() 

# Webhook'ni bir marta o'rnatish
# Vercel'da bu qismni o'chirib turamiz, chunki Vercel to'g'ridan-to'g'ri app.py'ni ishga tushirmaydi, 
# balki faqat 'webhook_handler' ni chaqiradi.
# Shuning uchun bu sozlashni Vercel'da joylashtirgandan keyin alohida script orqali qilsa yaxshi.

# Vercel ishga tushirganda, u faqat 'app' obyekti orqali ishlaydi.
# Shuning uchun 'if __name__ == "__main__":' qismi bu yerda kerak emas.

# application.run_polling() kodi butunlay olib tashlandi!