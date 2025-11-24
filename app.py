# app.py

import logging
import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask, request, jsonify
from collections import defaultdict

# ============ MUHIM IMPORTLAR ============
# config.py dan keladigan barcha maxfiy kalitlar os.getenv() orqali olinadi
from config import BOT_TOKEN, REQUIRED_CHANNEL, CONTACT_INFO, IMAGE_DIR, USER_DATA_FILE, REFERRAL_DATA_FILE, REFERRAL_BONUS, WEBHOOK_PATH
from database.universities_data import UNIVERSITIES
from languages import uz_latin, uz_cyrillic, english, korean
from utils.helpers import is_subscribed_to_channel, generate_referral_code, format_contact_info

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Har bir user uchun oxirgi xabar ID
last_messages = {}

# User ma'lumotlarini saqlash (Vercel'da faqat o'qish uchun)
user_data = {}
referral_data = {}

# Tillarni yuklaash
LANGUAGE_MODULES = {
    "uz": uz_latin,
    "uzb": uz_cyrillic,
    "en": english,
    "ko": korean
}

# ============ FAYL ISHLASH FUNKSIYALARI - VERCEL UCHUN O'ZGARTIRILDI (FAQAT O'QISH) ============

def load_user_data():
    """User va referal ma'lumotlarini yuklash (Faqat o'qish, yozishdagi xato olib tashlandi!)"""
    global user_data, referral_data
    
    # 1. User Data yuklash
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
    except Exception as e:
        logger.error(f"User data yuklashda xato (Faqat o'qish): {e}")
        user_data = {} 
    
    # 2. Referral Data yuklash
    try:
        if os.path.exists(REFERRAL_DATA_FILE):
            with open(REFERRAL_DATA_FILE, 'r', encoding='utf-8') as f:
                referral_data = json.load(f)
    except Exception as e:
        logger.error(f"Referral data yuklashda xato (Faqat o'qish): {e}")
        referral_data = {} 

def save_user_data():
    """Vercelda ma'lumot saqlash o'chirildi! Bulutli DB ga o'ting."""
    logger.warning("Vercel'da ma'lumotlar saqlash (save_user_data) o'chirilgan!")
    pass

# ============ TILLAR ============

def get_user_language(user_id):
    """User tilini olish (default: uz). Vercel'da faqat joriy sessiya uchun ishlaydi."""
    return user_data.get(str(user_id), {}).get('language', 'uz')

def set_user_language(user_id, lang):
    """User tilini o'rnatish. Saqlash o'chirilgan."""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {}
    user_data[str(user_id)]['language'] = lang
    # save_user_data() O'CHIRILGAN

def get_text(user_id, key):
    """Tilga mos matnni olish"""
    lang = get_user_language(user_id)
    module = LANGUAGE_MODULES.get(lang, uz_latin)
    return module.TEXTS.get(key, key)

# ============ XABAR BOSHQARUVI ============

async def delete_previous_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Faqat oxirgi bot xabarini o'chirish"""
    if chat_id in last_messages:
        try:
            await context.bot.delete_message(chat_id, last_messages[chat_id])
            logger.info(f"✅ Eski xabar o'chirildi: {last_messages[chat_id]}")
        except Exception as e:
            logger.debug(f"Xabar o'chirilmadi: {e}")

async def send_message_smart(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, 
                             reply_markup=None, photo_path=None):
    """Yangi xabar yuborish - eskisini o'chirib"""
    try:
        await delete_previous_message(context, chat_id) 
        
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo_file:
                sent = await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        else:
            sent = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        last_messages[chat_id] = sent.message_id
        logger.info(f"📤 Yangi xabar: {sent.message_id}")
        return sent
        
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        return None

# ============ KEYBOARDS ============

def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
            InlineKeyboardButton("🇺🇿 Ўзбекча", callback_data='lang_uzb')
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇰🇷 한국어", callback_data='lang_ko')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard(user_id):
    t = lambda key: get_text(user_id, key)
    
    keyboard = [
        [
            InlineKeyboardButton(t('btn_prices'), callback_data='info_prices'),
            InlineKeyboardButton(t('btn_universities'), callback_data='info_universities')
        ],
        [
            InlineKeyboardButton(t('btn_study'), callback_data='info_study'),
            InlineKeyboardButton(t('btn_contact'), callback_data='info_contact')
        ],
        [
            InlineKeyboardButton(t('btn_referral'), callback_data='info_referral'),
            InlineKeyboardButton(t('btn_settings'), callback_data='settings')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_university_keyboard(user_id):
    t = lambda key: get_text(user_id, key)
    lang = get_user_language(user_id)
    
    keyboard = []
    for uni_key, uni_data in UNIVERSITIES.items():
        uni_name = uni_data.get(f'name_{lang}', uni_data['name_uz'])
        keyboard.append([InlineKeyboardButton(uni_name, callback_data=f'uni_{uni_key}')])
    
    keyboard.append([InlineKeyboardButton(t('back_to_menu'), callback_data='start')])
    return InlineKeyboardMarkup(keyboard)

def get_university_detail_keyboard(user_id, uni_key):
    t = lambda key: get_text(user_id, key)
    
    keyboard = [
        [InlineKeyboardButton(t('btn_location'), callback_data=f'loc_{uni_key}')],
        [InlineKeyboardButton(t('uni_back_to_list'), callback_data='info_universities')],
        [InlineKeyboardButton(t('back_to_menu'), callback_data='start')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(user_id):
    t = lambda key: get_text(user_id, key)
    keyboard = [[InlineKeyboardButton(t('back_to_menu'), callback_data='start')]]
    return InlineKeyboardMarkup(keyboard)

# ============ SUBSCRIPTION CHECK ============

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kanal obunasini tekshirish"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if await is_subscribed_to_channel(context.bot, user_id, REQUIRED_CHANNEL):
        return True
    
    t = lambda key: get_text(user_id, key)
    
    keyboard = [
        [InlineKeyboardButton(t('subscribe_button'), url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")],
        [InlineKeyboardButton(t('check_subscription'), callback_data='check_sub')]
    ]
    
    await send_message_smart(
        context,
        chat_id,
        t('subscribe_required'),
        InlineKeyboardMarkup(keyboard)
    )
    return False


# ============ COMMAND HANDLERS ============

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message_before: str = None) -> None:
    """Asosiy menyuni yuborish uchun yordamchi funksiya"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    t = lambda key: get_text(user_id, key)
    welcome_text = t('welcome').format(name=user_name)
    
    final_text = ""
    if message_before:
        final_text += f"{message_before}\n\n"
        
    final_text += f"{welcome_text}\n\n{t('main_menu')}"
    
    await send_message_smart(
        context,
        chat_id,
        final_text,
        get_main_keyboard(user_id)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    # Referal kodini tekshirish (Saqlash qismi o'chirilgan)
    if update.message and context.args:
        ref_code = context.args[0].replace('ref_', '')
        if ref_code != str(user_id): 
             logger.info(f"Yangi user: {user_id} | Referred by: {ref_code} (Saqlanmadi)")
    
    # Til tanlanmaganmi?
    if str(user_id) not in user_data or 'language' not in user_data[str(user_id)]:
        text = "🌍 Tilni tanlang / Choose Language / Выберите язык / 언어를 선택하세요:"
        await send_message_smart(context, chat_id, text, get_language_keyboard())
        return
    
    # Kanal obunasini tekshirish
    if not await check_subscription(update, context):
        return
    
    # Asosiy menyu
    t = lambda key: get_text(user_id, key)
    welcome_text = t('welcome').format(name=user_name)
    
    await send_message_smart(
        context,
        chat_id,
        f"{welcome_text}\n\n{t('main_menu')}",
        get_main_keyboard(user_id)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline tugmalarni bosish hodisalarini boshqaradi"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = query.data
    
    t = lambda key: get_text(user_id, key)
    
    try:
        # Til tanlash
        if data.startswith('lang_'):
            lang = data.replace('lang_', '')
            set_user_language(user_id, lang) 
            
            if str(user_id) not in user_data or 'referral_code' not in user_data[str(user_id)]:
                ref_code = generate_referral_code(user_id)
                if str(user_id) not in user_data:
                    user_data[str(user_id)] = {}
                user_data[str(user_id)]['referral_code'] = ref_code
            
            await send_main_menu(update, context, t('language_changed'))
            return
        
        # Obuna tekshirish
        if data == 'check_sub':
            if await is_subscribed_to_channel(context.bot, user_id, REQUIRED_CHANNEL):
                user_name = query.from_user.first_name
                t = lambda key: get_text(user_id, key)
                welcome_text = t('welcome').format(name=user_name)
                
                await send_message_smart(
                    context,
                    chat_id,
                    f"{t('subscription_confirmed')}\n\n{welcome_text}\n\n{t('main_menu')}",
                    get_main_keyboard(user_id)
                )
                
            else:
                await send_message_smart(
                    context,
                    chat_id,
                    t('not_subscribed'), 
                    query.message.reply_markup 
                )
            return
        
        # Kanal obunasini tekshirish (boshqa tugmalar uchun)
        if not await check_subscription(update, context):
            return
        
        # Asosiy menyu
        if data == 'start':
            await send_main_menu(update, context) 
        
        # Narxlar
        elif data == 'info_prices':
            response = t('prices_title')
            response += t('prices_advance') + "\n"
            response += t('prices_advance_amount') + "\n"
            response += t('prices_advance_terms') + "\n"
            response += t('prices_final') + "\n"
            response += t('prices_final_amount') + "\n"
            response += t('prices_final_terms')
            response += t('prices_includes')
            
            await send_message_smart(context, chat_id, response, get_back_keyboard(user_id))
        
        # Universitetlar ro'yxati
        elif data == 'info_universities':
            response = t('universities_title')
            await send_message_smart(context, chat_id, response, get_university_keyboard(user_id))
            
        # Til kurslari
        elif data == 'info_study':
            await send_message_smart(context, chat_id, t('study_info'), get_back_keyboard(user_id))
            
        # Aloqa
        elif data == 'info_contact':
            lang = get_user_language(user_id)
            response = format_contact_info(CONTACT_INFO, lang)
            await send_message_smart(context, chat_id, response, get_back_keyboard(user_id))
            
        # Referal
        elif data == 'info_referral':
            ref_code = user_data.get(str(user_id), {}).get('referral_code', 'ERROR') 
            ref_stats = {'invited': 'N/A', 'confirmed': 'N/A', 'discount': 'N/A'} 
            
            bot_username = (await context.bot.get_me()).username
            ref_link = f"https://t.me/{bot_username}?start=ref_{ref_code}"
            
            response = t('referral_info').format(
                code=ref_code,
                invited=ref_stats['invited'],
                confirmed=ref_stats['confirmed'],
                discount=ref_stats['discount'],
                link=ref_link
            )
            
            keyboard = [
                [InlineKeyboardButton(t('referral_share'), url=f"https://t.me/share/url?url={ref_link}&text=Go Korea bilan Koreada o'qing!")],
                [InlineKeyboardButton(t('back_to_menu'), callback_data='start')]
            ]
            await send_message_smart(context, chat_id, response, InlineKeyboardMarkup(keyboard))
        
        # Sozlamalar
        elif data == 'settings':
            keyboard = [
                [InlineKeyboardButton(t('btn_change_language'), callback_data='change_lang')],
                [InlineKeyboardButton(t('back_to_menu'), callback_data='start')]
            ]
            await send_message_smart(context, chat_id, t('settings_menu'), InlineKeyboardMarkup(keyboard))
        
        elif data == 'change_lang':
            await send_message_smart(context, chat_id, t('choose_language'), get_language_keyboard())
        
        # Universitet tanlash
        elif data.startswith('uni_'):
            uni_key = data.replace('uni_', '')
            if uni_key in UNIVERSITIES:
                uni_data = UNIVERSITIES[uni_key]
                lang = get_user_language(user_id)
                
                uni_name = uni_data.get(f'name_{lang}', uni_data['name_uz'])
                programs = "\n".join(uni_data.get(f'programs_{lang}', uni_data['programs_uz']))
                advantages = "\n".join(uni_data.get(f'advantages_{lang}', uni_data['advantages_uz']))
                description = uni_data.get(f'description_{lang}', uni_data['description_uz'])
                admission = uni_data.get(f'admission_{lang}', uni_data['admission_uz'])

                caption = t('uni_info_template').format(
                    name=uni_name,
                    city=uni_data['city'],
                    price=uni_data['price'],
                    founded=uni_data['founded'],
                    students=uni_data['students'],
                    description=description,
                    programs=programs,
                    dormitory=uni_data['dormitory'],
                    advantages=advantages,
                    admission=admission
                )
                
                image_path = os.path.join(IMAGE_DIR, uni_data['rasm_fayli'])
                await send_message_smart(
                    context,
                    chat_id,
                    caption,
                    get_university_detail_keyboard(user_id, uni_key),
                    image_path if os.path.exists(image_path) else None
                )
        
        # Joylashuv
        elif data.startswith('loc_'):
            uni_key = data.replace('loc_', '')
            if uni_key in UNIVERSITIES:
                location = UNIVERSITIES[uni_key]['location']
                lang = get_user_language(user_id)
                
                city_description = location.get(f'city_description_{lang}', location['city_description_uz'])
                climate = location.get(f'climate_{lang}', location['climate_uz'])
                transport = location.get(f'transport_{lang}', location['transport_uz'])
                cost = location.get(f'monthly_cost_{lang}', location['monthly_cost_uz'])


                response = t('location_template').format(
                    city=UNIVERSITIES[uni_key]['city'],
                    description=city_description,
                    climate=climate,
                    transport=transport,
                    cost=cost,
                    address=location['address']
                )
                
                keyboard = [
                    [InlineKeyboardButton("📍 Google Maps", url=location['google_maps'])],
                    [InlineKeyboardButton(t('uni_back_to_list'), callback_data='info_universities')],
                    [InlineKeyboardButton(t('back_to_menu'), callback_data='start')]
                ]
                await send_message_smart(context, chat_id, response, InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logger.error(f"button_handler xatolik: {e}")
        await send_message_smart(
            context,
            chat_id,
            t('error_occurred'),
            get_main_keyboard(user_id)
        )

# ============ FLASK / VERCEL MANTIQI ============

# Barcha ma'lumotlarni yuklashni faqat bir marta boshlanganda chaqiramiz
load_user_data() 

# Flask ilovasini yaratish
app = Flask(__name__)

# Bot Application'ni yaratish (Global darajada)
application = Application.builder().token(BOT_TOKEN).build()

# Handlerlarni qo'shish
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))


@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_handler():
    """Telegramdan kelgan yangilanishlarni qabul qilish."""
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), application.bot)
            
            # Webhook'ni ishlashi uchun zarur (Context'ni ishga tushirish)
            async with application:
                await application.process_update(update)
            
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.error(f"Webhook process xatosi: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error"}), 405

@app.route('/', methods=['GET'])
def index():
    """Vercel'da ishlayotganini tekshirish uchun."""
    return 'Go Korea AI Bot is running on Webhook mode!'

# ============ YAKUN ============