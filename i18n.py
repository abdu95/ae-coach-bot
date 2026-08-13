# UI text translations. Claude's own analysis/roadmap output is not
# translated yet — only the bot's own static messages.

WELCOME = {
    "en": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ Upload your CV as a PDF\n"
        "2️⃣ Paste the job description you are targeting\n"
        "3️⃣ I analyse your CV against it step by step\n\n"
        "📄 <b>Upload your CV to begin.</b>"
    ),
    "uz": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ CV'ingizni PDF formatida yuklang\n"
        "2️⃣ Maqsad qilgan ish tavsifini (job description) joylashtiring\n"
        "3️⃣ Men CV'ingizni bosqichma-bosqich tahlil qilaman\n\n"
        "📄 <b>Boshlash uchun CV'ingizni yuklang.</b>"
    ),
    "ru": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ Загрузите своё резюме (CV) в формате PDF\n"
        "2️⃣ Вставьте описание вакансии, на которую претендуете\n"
        "3️⃣ Я проанализирую ваше резюме по шагам\n\n"
        "📄 <b>Загрузите резюме, чтобы начать.</b>"
    ),
}

CV_RECEIVED = {
    "en": (
        "✅ CV received.\n\n"
        "Now find the job posting you're targeting, copy its full job description text, "
        "and paste it here."
    ),
    "uz": (
        "✅ CV qabul qilindi.\n\n"
        "Endi maqsad qilgan ish e'lonini toping, uning to'liq tavsif matnini nusxalab oling "
        "va bu yerga joylashtiring."
    ),
    "ru": (
        "✅ Резюме получено.\n\n"
        "Теперь найдите вакансию, на которую претендуете, скопируйте полный текст описания "
        "вакансии и вставьте его сюда."
    ),
}

ANALYZING = {
    "en": (
        "🔍 <b>Analysing your CV against this role…</b>\n\n"
        "Here's what I'm doing:\n"
        "1️⃣ Checking your CV against the job's keywords (ATS Score)\n"
        "2️⃣ Checking your bullet points against the XYZ formula\n"
        "3️⃣ Mapping your skills against the tools this role needs\n"
        "4️⃣ Assessing your seniority level for this role\n\n"
        "This produces a 4-part breakdown, then a personalised roadmap. "
        "Usually takes about 20–30 seconds — hang tight."
    ),
    "uz": (
        "🔍 <b>CV'ingiz ushbu lavozim bo'yicha tahlil qilinmoqda…</b>\n\n"
        "Nima qilyapman:\n"
        "1️⃣ CV'ingizni vakansiya kalit so'zlari bilan solishtiryapman (ATS ball)\n"
        "2️⃣ Har bir bandni XYZ formulasi bo'yicha tekshiryapman\n"
        "3️⃣ Ko'nikmalaringizni ushbu lavozim talab qiladigan vositalar bilan solishtiryapman\n"
        "4️⃣ Ushbu lavozim uchun darajangizni baholayman\n\n"
        "Natijada 4 qismli tahlil, so'ng shaxsiy yo'l xaritasi (roadmap) tayyor bo'ladi. "
        "Odatda 20–30 soniya vaqt oladi — biroz kuting."
    ),
    "ru": (
        "🔍 <b>Анализирую ваше резюме под эту вакансию…</b>\n\n"
        "Что я делаю:\n"
        "1️⃣ Сравниваю резюме с ключевыми словами вакансии (ATS-балл)\n"
        "2️⃣ Проверяю пункты резюме по формуле XYZ\n"
        "3️⃣ Сопоставляю ваши навыки с инструментами, нужными для роли\n"
        "4️⃣ Оцениваю ваш уровень (грейд) для этой позиции\n\n"
        "В результате — разбор из 4 частей, а затем персональный план действий. "
        "Обычно занимает около 20–30 секунд — подождите немного."
    ),
}

LIMIT_REACHED = {
    "en": (
        "🚦 <b>You've used all {limit} free checks.</b>\n\n"
        "We're working on making more checks available (including paid options). "
        "Tap below to join the waitlist and we'll notify you here as soon as that's ready."
    ),
    "uz": (
        "🚦 <b>Siz barcha {limit} ta bepul tekshiruvdan foydalandingiz.</b>\n\n"
        "Ko'proq tekshiruvlarni (shu jumladan pullik variantlarni) taqdim etish ustida ishlayapmiz. "
        "Kutish ro'yxatiga qo'shilish uchun pastdagi tugmani bosing — tayyor bo'lishi bilan shu yerda xabar beramiz."
    ),
    "ru": (
        "🚦 <b>Вы использовали все {limit} бесплатных проверок.</b>\n\n"
        "Мы работаем над тем, чтобы открыть больше проверок (в том числе платных). "
        "Нажмите кнопку ниже, чтобы встать в список ожидания — мы сообщим здесь, как только это будет готово."
    ),
}

JOIN_WAITLIST_BUTTON = {
    "en": "🔔 Join waitlist",
    "uz": "🔔 Kutish ro'yxatiga qo'shilish",
    "ru": "🔔 Встать в список ожидания",
}

WAITLIST_JOINED = {
    "en": "✅ You're on the waitlist! We'll message you here as soon as more checks are available.",
    "uz": "✅ Siz kutish ro'yxatiga qo'shildingiz! Ko'proq tekshiruvlar mavjud bo'lishi bilan sizga shu yerda xabar beramiz.",
    "ru": "✅ Вы в списке ожидания! Мы напишем вам здесь, как только станет доступно больше проверок.",
}

CHECKS_LEFT = {
    "en": "({remaining}/{limit} free checks left)",
    "uz": "({remaining}/{limit} bepul tekshiruv qoldi)",
    "ru": "(осталось {remaining}/{limit} бесплатных проверок)",
}

ANALYSIS_DONE_CONTINUE = {
    "en": (
        "✅ This is the end of the analysis. Apply the tips above to your job application, "
        "or send /reset to check another job posting.\n\n({remaining}/{limit} checks left)"
    ),
    "uz": (
        "✅ Tahlil yakunlandi. Yuqoridagi tavsiyalarni ariza topshirishda qo'llang, "
        "yoki boshqa lavozimni tekshirish uchun /reset yuboring.\n\n({remaining}/{limit} tekshiruv qoldi)"
    ),
    "ru": (
        "✅ Анализ завершён. Примените советы выше в своей заявке, "
        "или отправьте /reset, чтобы проверить другую вакансию.\n\n(осталось {remaining}/{limit} проверок)"
    ),
}

ANALYSIS_DONE_LIMIT = {
    "en": (
        "✅ This is the end of the analysis. Apply the tips above to your job application.\n\n"
        "You've used all {limit} free checks. Want to check another role? "
        "Join the waitlist below and we'll notify you when more checks are available."
    ),
    "uz": (
        "✅ Tahlil yakunlandi. Yuqoridagi tavsiyalarni ariza topshirishda qo'llang.\n\n"
        "Siz barcha {limit} ta bepul tekshiruvdan foydalandingiz. Yana tekshirmoqchimisiz? "
        "Ko'proq tekshiruvlar mavjud bo'lganda xabar berishimiz uchun pastdagi kutish ro'yxatiga qo'shiling."
    ),
    "ru": (
        "✅ Анализ завершён. Примените советы выше в своей заявке.\n\n"
        "Вы использовали все {limit} бесплатных проверок. Хотите проверить ещё одну вакансию? "
        "Встаньте в список ожидания ниже — мы сообщим, когда будет доступно больше проверок."
    ),
}

PILOT_ENROLLED = {
    "en": "🎓 You're in the School21 pilot! You now have {quota} free checks.",
    "uz": "🎓 Siz School21 pilot dasturiga qo'shildingiz! Endi sizda {quota} ta bepul tekshiruv mavjud.",
    "ru": "🎓 Вы в пилоте School21! Теперь у вас {quota} бесплатных проверок.",
}

PILOT_ALREADY = {
    "en": "✅ You're already enrolled in the School21 pilot.",
    "uz": "✅ Siz allaqachon School21 pilot dasturida ro'yxatdan o'tgansiz.",
    "ru": "✅ Вы уже участвуете в пилоте School21.",
}

PILOT_FULL = {
    "en": "The School21 pilot is full, but you can still use your free checks below.",
    "uz": "School21 pilot dasturi to'lgan, lekin bepul tekshiruvlaringizdan pastda foydalanishingiz mumkin.",
    "ru": "Пилот School21 заполнен, но вы всё ещё можете использовать бесплатные проверки ниже.",
}

ROADMAP_WAIT_NOTE = {
    "en": "Usually takes about 15–20 seconds.",
    "uz": "Odatda 15–20 soniya vaqt oladi.",
    "ru": "Обычно занимает 15–20 секунд.",
}

# Keyed by the English block title from prompts.ROADMAP_BLOCKS — titles
# themselves stay in English (the header), only the description below
# them is translated.
ROADMAP_ITEM_DESC = {
    "CV Fixes": {
        "en": "Finding the top 5 changes that will make your CV match this role better, with before/after rewrites.",
        "uz": "CV'ingizni ushbu lavozimga yaqinlashtiradigan eng muhim 5 ta o'zgarishni topyapman, oldin/keyin qayta yozilgan variantlar bilan.",
        "ru": "Ищу топ-5 изменений, которые приблизят ваше резюме к этой вакансии, с примерами «было / стало».",
    },
    "Interview Prep": {
        "en": "Building your phone-screen opening line and a prioritised list of technical topics to study, based on this role's requirements.",
        "uz": "Telefon suhbati uchun ochilish gapini va ushbu lavozim talablariga asoslangan o'rganish mavzular ro'yxatini tayyorlayapman.",
        "ru": "Готовлю фразу для открытия телефонного интервью и приоритетный список тем для подготовки, исходя из требований вакансии.",
    },
    "Target Companies": {
        "en": "Putting together a shortlist of companies and role types that fit your profile and this target role.",
        "uz": "Profilingiz va maqsadli lavozimga mos keladigan kompaniyalar va lavozim turlari ro'yxatini tuzyapman.",
        "ru": "Составляю список компаний и типов должностей, подходящих под ваш профиль и целевую роль.",
    },
    "3-Month Plan": {
        "en": "Building a month-by-month plan to close the gap between your CV and this role.",
        "uz": "CV'ingiz va ushbu lavozim o'rtasidagi farqni yopish uchun oy-oy reja tuzyapman.",
        "ru": "Составляю помесячный план, чтобы закрыть разрыв между вашим резюме и этой вакансией.",
    },
    "Portfolio Project": {
        "en": "Designing one focused portfolio project that proves you can do this role.",
        "uz": "Ushbu lavozimni bajara olishingizni isbotlaydigan bitta aniq portfolio loyihasini ishlab chiqyapman.",
        "ru": "Продумываю один фокусный pet-проект для портфолио, который докажет, что вы готовы к этой роли.",
    },
    "Stepping-Stone Roles": {
        "en": "Finding realistic roles you can land now on the way to this target role.",
        "uz": "Maqsadli lavozimga yo'lda hozir egallashingiz mumkin bo'lgan real lavozimlarni topyapman.",
        "ru": "Ищу реальные позиции, которые можно получить уже сейчас на пути к целевой роли.",
    },
}


def t(key: str, lang: str) -> str:
    entry = STRINGS[key]
    return entry.get(lang) or entry["en"]


STRINGS = {
    "welcome": WELCOME,
    "cv_received": CV_RECEIVED,
    "analyzing": ANALYZING,
    "roadmap_wait": ROADMAP_WAIT_NOTE,
    "join_waitlist_button": JOIN_WAITLIST_BUTTON,
    "waitlist_joined": WAITLIST_JOINED,
    "pilot_already": PILOT_ALREADY,
    "pilot_full": PILOT_FULL,
}


def roadmap_loading(item: int, title: str, lang: str) -> str:
    desc_map = ROADMAP_ITEM_DESC.get(title, {})
    desc = desc_map.get(lang) or desc_map.get("en") or "Building this section..."
    wait = t("roadmap_wait", lang)
    return f"<b>🗺 Step 5 — Action Item {item}: {title}</b>\n\n⏳ {desc}\n\n{wait}"


def pilot_enrolled(quota: int, lang: str) -> str:
    template = PILOT_ENROLLED.get(lang) or PILOT_ENROLLED["en"]
    return template.format(quota=quota)


def limit_reached(limit: int, lang: str) -> str:
    template = LIMIT_REACHED.get(lang) or LIMIT_REACHED["en"]
    return template.format(limit=limit)


def checks_left(remaining: int, limit: int, lang: str) -> str:
    template = CHECKS_LEFT.get(lang) or CHECKS_LEFT["en"]
    return template.format(remaining=remaining, limit=limit)


def analysis_done(remaining: int, limit: int, lang: str) -> str:
    if remaining <= 0:
        template = ANALYSIS_DONE_LIMIT.get(lang) or ANALYSIS_DONE_LIMIT["en"]
        return template.format(limit=limit)
    template = ANALYSIS_DONE_CONTINUE.get(lang) or ANALYSIS_DONE_CONTINUE["en"]
    return template.format(remaining=remaining, limit=limit)
