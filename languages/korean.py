# 한국어 - KOREAN LANGUAGE

TEXTS = {
    # 일반
    "welcome": "안녕하세요, {name}님! 👋\n\n저는 'Go Korea Consulting'의 가상 비서입니다. 한국 유학, 대학교, 학비 등에 대해 도와드리겠습니다!",
    
    "choose_language": "🌍 언어를 선택하세요 / Choose Language:",
    "language_changed": "✅ 언어가 변경되었습니다!",
    "back_to_menu": "🏠 메인 메뉴",
    
    # 채널 구독
    "subscribe_required": "📢 봇을 사용하려면 먼저 채널을 구독해주세요!\n\n👇 아래 버튼을 클릭하세요:",
    "subscribe_button": "📢 채널 구독하기",
    "check_subscription": "✅ 구독 확인",
    "not_subscribed": "❌ 아직 구독하지 않으셨습니다!\n\n채널을 먼저 구독하고 '✅ 구독 확인' 버튼을 클릭해주세요.",
    "subscription_confirmed": "✅ 감사합니다! 이제 봇을 사용하실 수 있습니다.",
    
    # 메인 메뉴
    "main_menu": "필요한 섹션을 선택해주세요:",
    "btn_prices": "💰 가격 및 결제",
    "btn_universities": "🎓 대학교",
    "btn_study": "🇰🇷 어학 코스/서류",
    "btn_contact": "📞 연락처",
    "btn_referral": "🎁 추천 프로그램",
    "btn_settings": "⚙️ 설정",
    
    # 가격
    "prices_title": "💳 **Go Korea Consulting 서비스 가격:**\n\n",
    "prices_advance": "**1. 선불 (계약 및 서류):**",
    "prices_advance_amount": "금액: **2,000,000 UZS**",
    "prices_advance_terms": "계약 체결일에 지불. 비자 발급까지 추가 결제 불필요.",
    "prices_final": "\n**2. 최종 결제 (대행사 서비스 수수료):**",
    "prices_final_amount": "금액: **1,900 USD**",
    "prices_final_terms": "비자 수령 후 지불 (2월-3월).",
    "prices_includes": "\nℹ️ **컨설팅 서비스 포함 사항:**\n한국 대학 서류 제출, 입학 절차 전체 관리, 비자 지원. 아포스티유, 번역 등 모든 필요 비용이 선불에 포함됩니다.",
    
    # 대학교
    "universities_title": "🎓 **파트너 대학교**\n\n어느 대학에 대해 알고 싶으세요?",
    "uni_back_to_list": "⬅️ 대학 목록으로",
    "btn_location": "📍 위치 정보",
    
    # 대학 정보 템플릿
    "uni_info_template": """🎓 **{name}**

📍 **도시:** {city}
💵 **학비 (학기당):** {price}
📅 **설립:** {founded}
👥 **총 학생 수:** {students}

📖 **설명:**
{description}

✨ **주요 프로그램:**
{programs}

🏠 **기숙사:** {dormitory}

⭐ **장점:**
{advantages}

🛂 **입학:** {admission}""",

    # 위치
    "location_template": """📍 **{city} 정보**

{description}

🌡️ **기후:** {climate}
🚇 **교통:** {transport}
💰 **월 생활비:** {cost}

📌 **대학 주소:**
{address}""",

    # 어학 코스
    "study_info": """🇰🇷 **한국어 코스 (D-4 비자):**

📅 **기간:** 6개월 (레벨당)
🗓️ **시작일:** 3월, 6월, 9월, 12월 (연 4회)
⏰ **수업 시간:** 주 5일, 하루 4시간 (오전 9시 - 오후 1시)
💵 **학비:** 1,500,000 KRW (1학기, 3개월)

📄 **필요 서류 (비자 신청용):**
1. 여권 스캔
2. 신분증 또는 내부 여권 스캔
3. 증명사진 3x4cm JPG 포맷 흰색 배경
4. 부모님 여권 스캔
5. 출생증명서 스캔
6. IELTS/TOPIK 증명서 (있는 경우)
7. 졸업장 원본
8. 2025년 졸업생: 1-7학기 성적표 및 재학증명서

✈️ **비자 종류:** 어학연수용 D-4 비자. 비자 신청 전 과정을 지원해드립니다.""",

    # 연락처
    "contact_info": """📞 **Go Korea Consulting - 연락처**

👤 **Telegram:**
{telegram_accounts}

📱 **전화:** {phone}

📢 **채널:** {channel}

⏰ **근무 시간:** 월요일-금요일, 오전 9시 - 오후 6시
📍 **주소:** 타슈켄트, 칠란조르 구""",

    # 추천 시스템
    "referral_info": """🎁 **추천 프로그램**

친구를 초대하고 할인을 받으세요!

📊 **통계:**
🆔 추천 코드: `{code}`
👥 초대한 사람: {invited}명
✅ 확인된 신청: {confirmed}명
💰 총 할인 금액: ${discount}

🎯 **작동 방식:**
• 친구가 링크로 등록: ~$100 할인
• 친구가 한국 유학 성공: ~$200 할인

🔗 **추천 링크:**
{link}

친구와 가족에게 공유하세요! 🚀""",

    "referral_share": "📤 링크 공유",
    
    # 설정
    "settings_menu": "⚙️ **설정**\n\n어떤 설정을 변경하시겠습니까?",
    "btn_change_language": "🌍 언어 변경",
    
    # 오류 메시지
    "error_occurred": "❌ 오류가 발생했습니다. 다시 시도해주세요.",
    "uni_not_found": "죄송합니다. 이 대학에 대한 정보를 찾을 수 없습니다.",
    "unknown_command": "죄송합니다. 명령을 이해하지 못했습니다. 메뉴 버튼을 사용해주세요.",
}