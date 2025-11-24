import hashlib
from telegram import Bot
from telegram.error import TelegramError

async def is_subscribed_to_channel(bot: Bot, user_id: int, channel_username: str) -> bool:
    """
    Foydalanuvchining kanalga obuna ekanligini tekshirish
    """
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        # Status: creator, administrator, member - obuna
        # Status: left, kicked - obuna emas
        return member.status in ['creator', 'administrator', 'member']
    except TelegramError as e:
        # Kanal topilmasa yoki botda huquq yo'q (masalan, admin emas)
        # Bunday holatda, foydalanuvchini obuna bo'lishga majburlash uchun False qaytaramiz.
        print(f"Kanal tekshirishda xatolik: {e}")
        return False  # <--- TUZATILGAN JOY: True o'rniga False

def generate_referral_code(user_id: int) -> str:
    """
    Unique referal kod generatsiya qilish
    """
    # User ID ni hash qilish
    hash_object = hashlib.md5(str(user_id).encode())
    return hash_object.hexdigest()[:8].upper()


def format_contact_info(contact_dict: dict, language: str = 'uz') -> str:
    """
    Aloqa ma'lumotlarini formatlash
    """
    telegram_list = "\n".join([f"   • {acc}" for acc in contact_dict['telegram_accounts']])
    
    if language == 'uz':
        response = f"""📞 **Go Korea Consulting - Aloqa**

👤 **Telegram:**
{telegram_list}

📱 **Telefon:** {contact_dict['phone']}

📢 **Kanalimiz:** {contact_dict['channel']}

⏰ **Ish vaqti:** Dushanba-Juma, 9:00 - 18:00
📍 **Manzil:** Toshkent sh., Chilonzor tumani"""
    
    elif language == 'uzb':
        response = f"""📞 **Go Korea Consulting - Алоқа**

👤 **Telegram:**
{telegram_list}

📱 **Телефон:** {contact_dict['phone']}

📢 **Каналимиз:** {contact_dict['channel']}

⏰ **Иш вақти:** Душанба-Жума, 9:00 - 18:00
📍 **Манзил:** Тошкент ш., Чилонзор тумани"""
    
    elif language == 'en':
        response = f"""📞 **Go Korea Consulting - Contact**

👤 **Telegram:**
{telegram_list}

📱 **Phone:** {contact_dict['phone']}

📢 **Channel:** {contact_dict['channel']}

⏰ **Working hours:** Monday-Friday, 9:00 - 18:00
📍 **Address:** Tashkent, Chilonzor district"""
    
    else:  # Korean
        response = f"""📞 **Go Korea Consulting - 연락처**

👤 **Telegram:**
{telegram_list}

📱 **전화:** {contact_dict['phone']}

📢 **채널:** {contact_dict['channel']}

⏰ **근무 시간:** 월-금, 9:00 - 18:00
📍 **주소:** 타슈켄트, 칠란조르 구"""
    
    return response


def format_price_info(language: str = 'uz') -> str:
    """
    Narxlar haqida ma'lumotni formatlash
    """
    if language == 'uz':
        return """💳 **Go Korea Konsalting Xizmatlari Narxlari:**

**1. Oldindan To'lov (Shartnoma va Hujjatlar uchun):**
   Summasi: **2,000,000 So'm**
   Shartnoma imzolangan kuni to'lanadi. Oldindan to'lovdan keyin VIZA chiqquniga qadar boshqa to'lov talab qilinmaydi.

**2. Oxirgi To'lov (Firma Xizmati uchun):**
   Summasi: **1900 USD**
   VIZA qo'lingizga tegganidan so'ng (Fevral-Mart oylarida) to'lanadi.

ℹ️ **Konsalting Xizmatiga Kiritilganlar:**
Koreya universitetlariga hujjat topshirish, qabul jarayonini to'liq nazorat qilish va viza olishda yordam berish. Hujjatlarni apostil, tarjima va boshqa kerakli xarajatlar oldindan to'lovga kiritilgan."""
    
    # TODO: Boshqa tillar uchun
    return format_price_info('uz')