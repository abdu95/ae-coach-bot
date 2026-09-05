# UI text translations. Claude's own analysis/roadmap output is not
# translated yet — only the bot's own static messages.

WELCOME = {
    "en": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ Upload your CV as a PDF or Word (.docx) file\n"
        "2️⃣ Paste the job description you are targeting\n"
        "3️⃣ I analyse your CV against it step by step\n\n"
        "📄 <b>Upload your CV to begin.</b>"
    ),
    "uz": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ CV'ingizni PDF yoki Word (.docx) formatida yuklang\n"
        "2️⃣ Maqsad qilgan ish tavsifini (job description) joylashtiring\n"
        "3️⃣ Men CV'ingizni bosqichma-bosqich tahlil qilaman\n\n"
        "📄 <b>Boshlash uchun CV'ingizni yuklang.</b>"
    ),
    "ru": (
        "👋 <b>Accepted AI</b>\n\n"
        "1️⃣ Загрузите своё резюме (CV) в формате PDF или Word (.docx)\n"
        "2️⃣ Вставьте описание вакансии, на которую претендуете\n"
        "3️⃣ Я проанализирую ваше резюме по шагам\n\n"
        "📄 <b>Загрузите резюме, чтобы начать.</b>"
    ),
}

ASK_NAME = {
    "en": (
        "Hi, my name is Accepted AI. I help you get accepted into your dream job — "
        "just like others who've already used this bot and landed their first-ever "
        "interview invite, or even a job offer! 🎉\n\n"
        "But first, how should I call you?"
    ),
    "uz": (
        "Salom, mening ismim Accepted AI. Men sizga orzuingizdagi ishga qabul qilinishda "
        "yordam beraman — xuddi ushbu botdan foydalangan boshqalar birinchi marta "
        "suhbatga (interview) taklif olgani, hattoki ish taklifini qabul qilgani kabi! 🎉\n\n"
        "Ammo avval, sizni qanday deb chaqiray?"
    ),
    "ru": (
        "Привет, меня зовут Accepted AI. Я помогаю получить работу мечты — как и другие, "
        "кто уже пользовался этим ботом и получил своё первое приглашение на собеседование "
        "или даже оффер! 🎉\n\n"
        "Но для начала, как мне вас называть?"
    ),
}

STATS_AND_PRIVACY = {
    "en": (
        "Alright {name}, we've got about 7 seconds — that's how much time recruiters "
        "spend scanning a CV on average. Also, in a recent study, 43% of rejections came "
        "from preventable issues — bad formatting, missing keywords, parsing errors — "
        "not real experience gaps.\n\n"
        "So as a first step, I need your CV.\n\n"
        "🔒 Btw, don't worry about privacy: your CV is only used to generate your report. "
        "It's never shared with recruiters or anyone else — wipe it anytime with /reset."
    ),
    "uz": (
        "Xo'p, {name}, bizda taxminan 7 soniya bor — ish beruvchilar CV'ga o'rtacha shuncha "
        "vaqt ajratishadi. Yana, so'nggi tadqiqotga ko'ra, rad javoblarining 43% aslida "
        "tajriba yetishmasligidan emas — balki noto'g'ri formatlash, kalit so'zlar yo'qligi "
        "va CV'ni tizim o'qiy olmasligidan kelib chiqadi.\n\n"
        "Shuning uchun birinchi qadam sifatida menga CV'ingiz kerak.\n\n"
        "🔒 Aytgancha, maxfiylik haqida xavotir olmang: CV'ingiz faqat hisobot tayyorlash "
        "uchun ishlatiladi. U ish beruvchilarga yoki boshqa hech kimga berilmaydi — "
        "xohlagan vaqtda /reset bilan o'chirib tashlashingiz mumkin."
    ),
    "ru": (
        "Хорошо, {name}, у нас есть около 7 секунд — именно столько рекрутёры в среднем "
        "тратят на просмотр резюме. Также, по данным недавнего исследования, 43% отказов "
        "связаны не с нехваткой опыта, а с исправимыми проблемами — плохим форматированием, "
        "отсутствием ключевых слов и ошибками при разборе резюме системой.\n\n"
        "Поэтому первым делом мне нужно ваше резюме.\n\n"
        "🔒 Кстати, не переживайте насчёт конфиденциальности: ваше резюме используется "
        "только для подготовки отчёта. Оно не передаётся рекрутёрам и никому другому — "
        "можете удалить его в любой момент командой /reset."
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

PAY_BUTTON = {
    "en": "💳 Pay {amount} UZS — 10 checks",
    "uz": "💳 To'lash — {amount} so'm — 10 ta tekshiruv",
    "ru": "💳 Оплатить {amount} сум — 10 проверок",
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

RESET_DONE = {
    "en": "🔄 Reset. Upload your CV to start again.",
    "uz": "🔄 Qayta boshlandi. Qaytadan boshlash uchun CV'ingizni yuklang.",
    "ru": "🔄 Сброшено. Загрузите резюме, чтобы начать заново.",
}

PLEASE_UPLOAD_CV = {
    "en": "Please upload a <b>PDF</b> or <b>Word (.docx)</b> file.",
    "uz": "Iltimos, <b>PDF</b> yoki <b>Word (.docx)</b> formatidagi faylni yuklang.",
    "ru": "Пожалуйста, загрузите файл в формате <b>PDF</b> или <b>Word (.docx)</b>.",
}

READING_CV = {
    "en": "📄 Reading your CV…",
    "uz": "📄 CV'ingiz o'qilmoqda…",
    "ru": "📄 Читаю ваше резюме…",
}

CV_READ_ERROR = {
    "en": "❌ Could not read your CV. Please try again.",
    "uz": "❌ CV'ingizni o'qib bo'lmadi. Qaytadan urinib ko'ring.",
    "ru": "❌ Не удалось прочитать резюме. Попробуйте ещё раз.",
}

WRONG_PHASE = {
    "en": "Send /start to begin or /reset to start over.",
    "uz": "Boshlash uchun /start, qaytadan boshlash uchun /reset yuboring.",
    "ru": "Отправьте /start, чтобы начать, или /reset, чтобы начать заново.",
}

JD_TOO_SHORT = {
    "en": "That looks too short. Please paste the full job description.",
    "uz": "Bu juda qisqa ko'rinyapti. Iltimos, ish tavsifining to'liq matnini joylashtiring.",
    "ru": "Это слишком коротко. Пожалуйста, вставьте полный текст описания вакансии.",
}

ANALYSIS_FAILED = {
    "en": "❌ Analysis failed. Send /reset and try again.",
    "uz": "❌ Tahlil amalga oshmadi. /reset yuboring va qaytadan urinib ko'ring.",
    "ru": "❌ Анализ не удался. Отправьте /reset и попробуйте снова.",
}

CHECK_WRITING_BUTTON = {
    "en": "Check my CV writing →",
    "uz": "CV yozuvimni tekshirish →",
    "ru": "Проверить стиль резюме →",
}

ROADMAP_FAILED = {
    "en": "❌ Roadmap generation failed. Send /reset to try again.",
    "uz": "❌ Yo'l xaritasini yaratib bo'lmadi. Qaytadan urinish uchun /reset yuboring.",
    "ru": "❌ Не удалось создать план действий. Отправьте /reset, чтобы попробовать снова.",
}

CONTINUE_BUTTON = {
    "en": "Continue: {title} →",
    "uz": "Davom etish: {title} →",
    "ru": "Продолжить: {title} →",
}

NEXT_FIX_BUTTON = {
    "en": "Next fix →",
    "uz": "Keyingi tuzatish →",
    "ru": "Следующая правка →",
}

SESSION_EXPIRED = {
    "en": "Session expired. Send /reset to start over.",
    "uz": "Sessiya muddati tugadi. Qaytadan boshlash uchun /reset yuboring.",
    "ru": "Сессия истекла. Отправьте /reset, чтобы начать заново.",
}

SKILL_GAPS_BUTTON = {
    "en": "See my skill gaps →",
    "uz": "Ko'nikma bo'shliqlarimni ko'rish →",
    "ru": "Посмотреть пробелы в навыках →",
}

ASSESS_LEVEL_BUTTON = {
    "en": "Assess my level →",
    "uz": "Darajamni baholash →",
    "ru": "Оценить мой уровень →",
}

GET_ROADMAP_BUTTON = {
    "en": "Get my roadmap →",
    "uz": "Yo'l xaritamni olish →",
    "ru": "Получить план действий →",
}

ROADMAP_WAIT_NOTE = {
    "en": "Usually takes about 15–20 seconds.",
    "uz": "Odatda 15–20 soniya vaqt oladi.",
    "ru": "Обычно занимает 15–20 секунд.",
}

APP_INTRO = {
    "en": "🔍 Search live vacancies matching a job title and location.",
    "uz": "🔍 Lavozim va joylashuvga mos vakansiyalarni qidiring.",
    "ru": "🔍 Ищите вакансии по должности и локации.",
}

APP_OPEN_BUTTON = {
    "en": "Open search", "uz": "Qidiruvni ochish", "ru": "Открыть поиск",
}

APP_NOT_CONFIGURED = {
    "en": "Mini App isn't configured yet.",
    "uz": "Mini ilova hali sozlanmagan.",
    "ru": "Мини-приложение ещё не настроено.",
}

JOBS_NEED_CV = {
    "en": "Please upload your CV first so I can suggest matching roles. 📄",
    "uz": "Mos lavozimlarni taklif qilishim uchun avval CV'ingizni yuklang. 📄",
    "ru": "Пожалуйста, сначала загрузите резюме, чтобы я мог предложить подходящие вакансии. 📄",
}

JOBS_FINDING_TITLES = {
    "en": "🔍 Analyzing your CV to find matching job titles…",
    "uz": "🔍 Mos lavozimlarni topish uchun CV'ingiz tahlil qilinmoqda…",
    "ru": "🔍 Анализирую резюме, чтобы подобрать подходящие должности…",
}

JOBS_TITLES_FAILED = {
    "en": "❌ Couldn't generate job title suggestions. Send /jobs to try again.",
    "uz": "❌ Lavozim takliflarini yaratib bo'lmadi. Qaytadan urinish uchun /jobs yuboring.",
    "ru": "❌ Не удалось подобрать варианты должностей. Отправьте /jobs, чтобы попробовать снова.",
}

JOBS_PICK_TITLE = {
    "en": "Which of these fits what you're looking for?",
    "uz": "Ulardan qaysi biri sizga mos keladi?",
    "ru": "Какой из вариантов вам подходит?",
}

JOBS_REGENERATE_BUTTON = {
    "en": "🔄 Suggest different titles",
    "uz": "🔄 Boshqa lavozimlarni taklif qilish",
    "ru": "🔄 Предложить другие варианты",
}

JOBS_ASK_LOCATION = {
    "en": "Which location? (e.g. Tashkent, Remote, Europe)",
    "uz": "Qaysi joylashuv? (masalan: Toshkent, Remote, Yevropa)",
    "ru": "Какая локация? (например: Ташкент, Remote, Европа)",
}

JOBS_ASK_WORK_SETUP = {
    "en": "What work setup do you want?",
    "uz": "Qanday ish formatini xohlaysiz?",
    "ru": "Какой формат работы вам нужен?",
}

WORK_SETUP_REMOTE = {"en": "🏠 Remote", "uz": "🏠 Masofaviy", "ru": "🏠 Удалённо"}
WORK_SETUP_HYBRID = {"en": "🔀 Hybrid", "uz": "🔀 Gibrid", "ru": "🔀 Гибрид"}
WORK_SETUP_ONSITE = {"en": "🏢 Onsite", "uz": "🏢 Ofisda", "ru": "🏢 В офисе"}

JOBS_ASK_INDUSTRY = {
    "en": "Any specific industry? (or tap Skip)",
    "uz": "Ma'lum bir soha bormi? (yoki O'tkazib yuborish tugmasini bosing)",
    "ru": "Есть предпочтения по отрасли? (или нажмите «Пропустить»)",
}

JOBS_INDUSTRY_SKIP_BUTTON = {
    "en": "Skip →",
    "uz": "O'tkazib yuborish →",
    "ru": "Пропустить →",
}

JOBS_SEARCHING = {
    "en": "🔎 Searching for a matching vacancy… usually takes 15–30 seconds.",
    "uz": "🔎 Mos vakansiya qidirilmoqda… odatda 15–30 soniya vaqt oladi.",
    "ru": "🔎 Ищу подходящую вакансию… обычно занимает 15–30 секунд.",
}

JOBS_SEARCH_FAILED = {
    "en": "❌ Search failed. Try again in a moment.",
    "uz": "❌ Qidiruv amalga oshmadi. Birozdan keyin qayta urinib ko'ring.",
    "ru": "❌ Поиск не удался. Попробуйте ещё раз через некоторое время.",
}

JOBS_NO_MATCH = {
    "en": "No matching posting found — try different criteria with /jobs.",
    "uz": "Mos e'lon topilmadi — /jobs orqali boshqa mezonlar bilan urinib ko'ring.",
    "ru": "Подходящая вакансия не найдена — попробуйте другие критерии через /jobs.",
}

JOBS_SEARCH_AGAIN_BUTTON = {
    "en": "🔄 Search again",
    "uz": "🔄 Qayta qidirish",
    "ru": "🔄 Искать снова",
}

JOBS_PICK_BUTTON = {
    "en": "✅ Pick this one",
    "uz": "✅ Shuni tanlash",
    "ru": "✅ Выбрать эту",
}

JOBS_SEARCH_CAP_REACHED = {
    "en": "You've reached the search limit for this session — pick one of the postings above, or send /jobs again later.",
    "uz": "Ushbu sessiya uchun qidiruv chegarasiga yetdingiz — yuqoridagi e'lonlardan birini tanlang yoki keyinroq qaytadan /jobs yuboring.",
    "ru": "Вы достигли лимита поиска на эту сессию — выберите одну из показанных вакансий или отправьте /jobs позже снова.",
}

JOBS_PICKED = {
    "en": "✅ Saved. This is now your target vacancy.",
    "uz": "✅ Saqlandi. Bu endi sizning maqsadli vakansiyangiz.",
    "ru": "✅ Сохранено. Это теперь ваша целевая вакансия.",
}

VACANCY_SEARCH_LABEL = {"en": "Search", "uz": "Qidiruv", "ru": "Поиск"}
VACANCY_MATCH_LABEL = {"en": "Match", "uz": "Moslik", "ru": "Соответствие"}
VACANCY_MATCHED_LABEL = {"en": "Matched", "uz": "Mos keldi", "ru": "Совпало"}
VACANCY_MISSING_LABEL = {"en": "Missing", "uz": "Yetishmayapti", "ru": "Отсутствует"}
VACANCY_VIEW_POSTING = {"en": "View job posting", "uz": "E'lonni ko'rish", "ru": "Посмотреть вакансию"}

STEP_HEADERS = {
    "ats": {
        "en": "📊 Step 1 — ATS Score",
        "uz": "📊 1-bosqich — ATS balli",
        "ru": "📊 Шаг 1 — ATS-балл",
    },
    "xyz": {
        "en": "✍️ Step 2 — XYZ Formula Check",
        "uz": "✍️ 2-bosqich — XYZ formulasi tekshiruvi",
        "ru": "✍️ Шаг 2 — Проверка по формуле XYZ",
    },
    "tools": {
        "en": "🛠 Step 3 — Skill Radar",
        "uz": "🛠 3-bosqich — Ko'nikmalar radari",
        "ru": "🛠 Шаг 3 — Радар навыков",
    },
    "level": {
        "en": "Step 4 — Level Assessment",
        "uz": "4-bosqich — Daraja baholash",
        "ru": "Шаг 4 — Оценка уровня",
    },
}

ROADMAP_STEP_LABEL = {
    "en": "Step 5 — Action Item {item}: {title}",
    "uz": "5-bosqich — {item}-band: {title}",
    "ru": "Шаг 5 — Пункт {item}: {title}",
}

# Translated display names for prompts.ROADMAP_BLOCKS titles. Keyed by the
# English title (the stable identifier used throughout the code) — the
# translation is only for what gets shown in the header.
ROADMAP_ITEM_TITLE = {
    "CV Fixes": {
        "en": "CV Fixes",
        "uz": "CV'dagi tuzatishlar",
        "ru": "Правки резюме",
    },
    "Phone Screen Prep": {
        "en": "Phone Screen Prep",
        "uz": "Telefon suhbatiga tayyorgarlik",
        "ru": "Подготовка к телефонному интервью",
    },
    "Technical Interview Prep": {
        "en": "Technical Interview Prep",
        "uz": "Texnik intervyuga tayyorgarlik",
        "ru": "Подготовка к техническому интервью",
    },
    "Target Companies": {
        "en": "Target Companies",
        "uz": "Maqsadli kompaniyalar",
        "ru": "Целевые компании",
    },
    "3-Month Plan": {
        "en": "3-Month Plan",
        "uz": "3 oylik reja",
        "ru": "План на 3 месяца",
    },
    "Portfolio Project": {
        "en": "Portfolio Project",
        "uz": "Portfolio loyihasi",
        "ru": "Проект для портфолио",
    },
    "Stepping-Stone Roles": {
        "en": "Stepping-Stone Roles",
        "uz": "Oraliq lavozimlar",
        "ru": "Промежуточные роли",
    },
}

# Keyed by the English block title from prompts.ROADMAP_BLOCKS — used to
# look up the description shown under the (now-translatable) header.
ROADMAP_ITEM_DESC = {
    "CV Fixes": {
        "en": "Finding the top 5 changes that will make your CV match this role better, with before/after rewrites.",
        "uz": "CV'ingizni ushbu lavozimga yaqinlashtiradigan eng muhim 5 ta o'zgarishni topyapman, oldin/keyin qayta yozilgan variantlar bilan.",
        "ru": "Ищу топ-5 изменений, которые приблизят ваше резюме к этой вакансии, с примерами «было / стало».",
    },
    "Phone Screen Prep": {
        "en": "Building your phone-screen opening line and how to position yourself, based on this role's requirements.",
        "uz": "Ushbu lavozim talablariga asoslanib, telefon suhbati uchun ochilish gapini va o'zingizni qanday taqdim etishni tayyorlayapman.",
        "ru": "Готовлю фразу для открытия телефонного интервью и то, как себя позиционировать, исходя из требований вакансии.",
    },
    "Technical Interview Prep": {
        "en": "Building a prioritised list of technical topics to study, based on this role's requirements.",
        "uz": "Ushbu lavozim talablariga asoslangan holda o'rganish uchun ustuvor texnik mavzular ro'yxatini tayyorlayapman.",
        "ru": "Составляю приоритетный список технических тем для подготовки, исходя из требований вакансии.",
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
    "reset_done": RESET_DONE,
    "ask_name": ASK_NAME,
    "please_upload_cv": PLEASE_UPLOAD_CV,
    "reading_cv": READING_CV,
    "cv_read_error": CV_READ_ERROR,
    "wrong_phase": WRONG_PHASE,
    "jd_too_short": JD_TOO_SHORT,
    "analysis_failed": ANALYSIS_FAILED,
    "check_writing_button": CHECK_WRITING_BUTTON,
    "roadmap_failed": ROADMAP_FAILED,
    "session_expired": SESSION_EXPIRED,
    "skill_gaps_button": SKILL_GAPS_BUTTON,
    "assess_level_button": ASSESS_LEVEL_BUTTON,
    "get_roadmap_button": GET_ROADMAP_BUTTON,
    "next_fix_button": NEXT_FIX_BUTTON,
    "app_intro": APP_INTRO,
    "app_open_button": APP_OPEN_BUTTON,
    "app_not_configured": APP_NOT_CONFIGURED,
    "jobs_need_cv": JOBS_NEED_CV,
    "jobs_finding_titles": JOBS_FINDING_TITLES,
    "jobs_titles_failed": JOBS_TITLES_FAILED,
    "jobs_pick_title": JOBS_PICK_TITLE,
    "jobs_regenerate_button": JOBS_REGENERATE_BUTTON,
    "jobs_ask_location": JOBS_ASK_LOCATION,
    "jobs_ask_work_setup": JOBS_ASK_WORK_SETUP,
    "work_setup_remote": WORK_SETUP_REMOTE,
    "work_setup_hybrid": WORK_SETUP_HYBRID,
    "work_setup_onsite": WORK_SETUP_ONSITE,
    "jobs_ask_industry": JOBS_ASK_INDUSTRY,
    "jobs_industry_skip_button": JOBS_INDUSTRY_SKIP_BUTTON,
    "jobs_searching": JOBS_SEARCHING,
    "jobs_search_failed": JOBS_SEARCH_FAILED,
    "jobs_no_match": JOBS_NO_MATCH,
    "jobs_search_again_button": JOBS_SEARCH_AGAIN_BUTTON,
    "jobs_pick_button": JOBS_PICK_BUTTON,
    "jobs_search_cap_reached": JOBS_SEARCH_CAP_REACHED,
    "jobs_picked": JOBS_PICKED,
    "vacancy_search_label": VACANCY_SEARCH_LABEL,
    "vacancy_match_label": VACANCY_MATCH_LABEL,
    "vacancy_matched_label": VACANCY_MATCHED_LABEL,
    "vacancy_missing_label": VACANCY_MISSING_LABEL,
    "vacancy_view_posting": VACANCY_VIEW_POSTING,
}


def step_header(key: str, lang: str) -> str:
    entry = STEP_HEADERS[key]
    return entry.get(lang) or entry["en"]


def roadmap_item_title(title: str, lang: str) -> str:
    entry = ROADMAP_ITEM_TITLE.get(title, {})
    return entry.get(lang) or entry.get("en") or title


def roadmap_header(item: int, title: str, lang: str) -> str:
    template = ROADMAP_STEP_LABEL.get(lang) or ROADMAP_STEP_LABEL["en"]
    label = template.format(item=item, title=roadmap_item_title(title, lang))
    return f"🗺 {label}"


def cv_fix_header(index: int, total: int, lang: str) -> str:
    return f"{roadmap_header(1, 'CV Fixes', lang)} ({index}/{total})"


def roadmap_loading(item: int, title: str, lang: str) -> str:
    desc_map = ROADMAP_ITEM_DESC.get(title, {})
    desc = desc_map.get(lang) or desc_map.get("en") or "Building this section..."
    wait = t("roadmap_wait", lang)
    return f"<b>{roadmap_header(item, title, lang)}</b>\n\n⏳ {desc}\n\n{wait}"


def pay_button(amount_tiyin: int, lang: str) -> str:
    template = PAY_BUTTON.get(lang) or PAY_BUTTON["en"]
    return template.format(amount=f"{amount_tiyin // 100:,}")


def continue_button(title: str, lang: str) -> str:
    template = CONTINUE_BUTTON.get(lang) or CONTINUE_BUTTON["en"]
    return template.format(title=title)


def pilot_enrolled(quota: int, lang: str) -> str:
    template = PILOT_ENROLLED.get(lang) or PILOT_ENROLLED["en"]
    return template.format(quota=quota)


def stats_and_privacy(name: str, lang: str) -> str:
    template = STATS_AND_PRIVACY.get(lang) or STATS_AND_PRIVACY["en"]
    return template.format(name=name)


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
