import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
from dotenv import load_dotenv
from collections import defaultdict

from data import Q_A_DATA, PRICES_INFO, UNIVERSITY_INFO, STUDY_INFO

# .env fayldan tokenni yuklash (XAVFSIZLIK!)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("⚠️ BOT_TOKEN topilmadi! .env faylni tekshiring.")

# Rasmlar papkasi manzili
IMAGE_DIR = 'images'

# Har bir chat uchun oxirgi bot xabar ID sini saqlash
last_bot_messages = defaultdict(list)

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_main_keyboard():
    """Asosiy menyu tugmalarini yaratish."""
    keyboard = [
        [
            InlineKeyboardButton("💰 Narxlar va To'lovlar", callback_data='info_prices'),
            InlineKeyboardButton("🎓 Universitetlar", callback_data='info_universities')
        ],
        [
            InlineKeyboardButton("🇰🇷 Til Kurslari/Hujjatlar", callback_data='info_study'),
            InlineKeyboardButton("📞 Aloqa", callback_data='info_contact')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_university_keyboard():
    """Universitetlar ro'yxati tugmalarini yaratish."""
    keyboard = []
    for uni_name in UNIVERSITY_INFO.keys():
        keyboard.append([InlineKeyboardButton(uni_name, callback_data=f'uni_{uni_name}')])
    
    keyboard.append([InlineKeyboardButton("⬅️ Asosiy Menyu", callback_data='start')])
    return InlineKeyboardMarkup(keyboard)


def format_uni_info(uni_name):
    """Bitta universitet haqidagi ma'lumotni formatlash."""
    uni_data = UNIVERSITY_INFO[uni_name]
    response = f"🎓 **{uni_name} Universiteti haqida ma'lumot:**\n\n"
    response += f"📍 Shahar: {uni_data['shahar']}\n"
    response += f"💵 Kontrakt Narxi (1 Semestr): **{uni_data['narx']}**\n"
    response += f"✍️ Tavsif: {uni_data['tavsif']}\n"
    response += f"✨ Afzalligi: {uni_data['afzallik']}\n"
    response += f"🛂 Qabul turi: **{uni_data['qabul_turi']}**\n"
    return response


def format_prices_info():
    """Narxlar haqidagi ma'lumotni formatlash."""
    price_info = PRICES_INFO["asosiy_konsalting"]
    
    response = "💳 **Go Korea Konsalting Xizmatlari Narxlari:**\n\n"
    response += "1. **Oldindan To'lov (Shartnoma va Hujjatlar uchun):**\n"
    response += f"   Summasi: **{price_info['oldindan_tolov']}**\n"
    response += f"   Shartlari: {price_info['oldindan_shart']}\n\n"
    
    response += "2. **Oxirgi To'lov (Firma Xizmati uchun):**\n"
    response += f"   Summasi: **{price_info['oxirgi_tolov']}**\n"
    response += f"   Shartlari: {price_info['oxirgi_shart']}\n\n"
    
    response += f"ℹ️ **Konsalting Xizmatiga Kiritilganlar:** {price_info['tavsif']}"
    return response


def format_study_info():
    """Til kurslari haqidagi ma'lumotni formatlash."""
    course_info = STUDY_INFO["til_kursi"]
    hujjat_list = "\n".join(STUDY_INFO['hujjat_talablari'])
    
    response = "🇰🇷 **Koreys Tili Kurslari (D-4 Viza):**\n\n"
    response += f"Davomiylik: **{course_info['davomiylik']}**\n"
    response += f"Boshlanish sanalari: {course_info['boshlanish']}\n"
    response += f"Dars vaqti: {course_info['dars_vaqti']}\n"
    response += f"Narx (Namuna): {course_info['narx']}\n\n"
    
    response += "📄 **Asosiy Hujjat Talablari (Viza uchun):**\n"
    response += hujjat_list
    
    return response


async def delete_all_bot_messages(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Saqlangan BARCHA eski bot xabarlarini o'chirish."""
    if chat_id in last_bot_messages:
        deleted = 0
        for msg_id in last_bot_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id, msg_id)
                deleted += 1
            except Exception as e:
                logger.debug(f"Xabar {msg_id} o'chirilmadi: {e}")
        
        # Ro'yxatni tozalash
        last_bot_messages[chat_id].clear()
        logger.info(f"✅ {deleted} ta eski xabar o'chirildi (Chat: {chat_id})")


async def send_and_track_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, 
                                 reply_markup=None, photo_path=None):
    """Yangi xabar yuborish va uning ID sini saqlash."""
    try:
        # Avval BARCHA eski xabarlarni o'chirish
        await delete_all_bot_messages(context, chat_id)
        
        # Yangi xabar yuborish
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo_file:
                sent_message = await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        else:
            sent_message = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        # Yangi xabar ID sini saqlash
        if sent_message:
            last_bot_messages[chat_id].append(sent_message.message_id)
            logger.info(f"📤 Yangi xabar yuborildi: {sent_message.message_id}")
        
        return sent_message
        
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        return None


# ----------------- COMMAND HANDLERS -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i kelganda asosiy menyuni yuboradi."""
    user_name = update.effective_user.first_name
    reply_text = (
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        "Men 'Go Korea Consulting' kompaniyasining virtual yordamchisiman. "
        "Kerakli bo'limni tanlash uchun quyidagi tugmalardan foydalaning."
    )
    
    try:
        if update.message:
            chat_id = update.message.chat_id
            await send_and_track_message(context, chat_id, reply_text, get_main_keyboard())
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
            await send_and_track_message(context, chat_id, reply_text, get_main_keyboard())
    except Exception as e:
        logger.error(f"Start funksiyasida xatolik: {e}")


async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/narxlar buyrug'iga javob beradi."""
    try:
        chat_id = update.message.chat_id
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]])
        await send_and_track_message(context, chat_id, format_prices_info(), reply_markup)
    except Exception as e:
        logger.error(f"cmd_prices xatolik: {e}")


async def cmd_universities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/universitetlar buyrug'iga javob beradi."""
    try:
        chat_id = update.message.chat_id
        response = "🎓 **Hamkor Universitetlarimiz**\n\nQaysi universitet haqida ma'lumot kerak?"
        await send_and_track_message(context, chat_id, response, get_university_keyboard())
    except Exception as e:
        logger.error(f"cmd_universities xatolik: {e}")


async def cmd_study(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/darslar buyrug'iga javob beradi."""
    try:
        chat_id = update.message.chat_id
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]])
        await send_and_track_message(context, chat_id, format_study_info(), reply_markup)
    except Exception as e:
        logger.error(f"cmd_study xatolik: {e}")


# ----------------- MESSAGE HANDLER -----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi yuborgan matnni qabul qiladi va ma'lumotlar bazasi orqali javob beradi."""
    user_text = update.message.text.lower()
    chat_id = update.message.chat_id
    response = ""
    reply_markup = None

    # Q_A_DATA dan javob qidirish
    for keyword, answer in Q_A_DATA.items():
        if keyword in user_text:
            response = answer
            break
    
    # Agar javob topilmasa
    if not response:
        response = "Kechirasiz, men savolingizga hozircha aniq javob bera olmadim. Iltimos, quyidagi asosiy menyu tugmalaridan foydalaning yoki *Aloqa* deb yozing."
        reply_markup = get_main_keyboard()

    try:
        await send_and_track_message(context, chat_id, response, reply_markup)
    except Exception as e:
        logger.error(f"handle_message xatolik: {e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline tugmalarni bosish hodisalarini boshqaradi."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id
    
    try:
        # Asosiy menyu
        if data == 'start':
            response = "Bosh menyudasiz. Kerakli bo'limni tanlang."
            await send_and_track_message(context, chat_id, response, get_main_keyboard())
        
        # Narxlar
        elif data == 'info_prices':
            response = format_prices_info()
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]])
            await send_and_track_message(context, chat_id, response, reply_markup)
        
        # Universitetlar ro'yxati
        elif data == 'info_universities':
            response = "🎓 **Hamkor Universitetlarimiz**\n\nQaysi universitet haqida ma'lumot kerak?"
            await send_and_track_message(context, chat_id, response, get_university_keyboard())
        
        # Til kurslari
        elif data == 'info_study':
            response = format_study_info()
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]])
            await send_and_track_message(context, chat_id, response, reply_markup)
        
        # Aloqa
        elif data == 'info_contact':
            response = Q_A_DATA.get('aloqa', 'Aloqa ma\'lumotlari topilmadi.')
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]])
            await send_and_track_message(context, chat_id, response, reply_markup)
        
        # Universitet tanlanganda (rasm bilan)
        elif data.startswith('uni_'):
            uni_name = data.replace('uni_', '')
            if uni_name in UNIVERSITY_INFO:
                uni_data = UNIVERSITY_INFO[uni_name]
                
                # Rasm yo'lini aniqlash
                image_filename = uni_data.get('rasm_fayli', 'default.jpg')
                image_path = os.path.join(IMAGE_DIR, image_filename)
                
                caption = format_uni_info(uni_name)
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Universitetlar Ro'yxati", callback_data='info_universities')],
                    [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data='start')]
                ])
                
                # Rasmni yuborish
                await send_and_track_message(
                    context, 
                    chat_id, 
                    caption, 
                    reply_markup, 
                    image_path if os.path.exists(image_path) else None
                )
            else:
                response = "Kechirasiz, bu universitet haqida ma'lumot topilmadi."
                await send_and_track_message(context, chat_id, response, get_main_keyboard())
    
    except Exception as e:
        logger.error(f"button_handler xatolik: {e}")
        try:
            await send_and_track_message(
                context,
                chat_id,
                "Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                get_main_keyboard()
            )
        except:
            pass


def main() -> None:
    """Botni ishga tushirish uchun asosiy funksiya."""
    
    application = Application.builder().token(TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("narxlar", cmd_prices))
    application.add_handler(CommandHandler("universitetlar", cmd_universities))
    application.add_handler(CommandHandler("darslar", cmd_study))

    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botni ishga tushirish
    logger.info("✅ Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()