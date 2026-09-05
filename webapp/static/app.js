// ── i18n ─────────────────────────────────────────────────────────────
const I18N = {
  nav_applications: { en: "📋 My Applications", uz: "📋 Arizalarim", ru: "📋 Мои заявки" },
  greeting: { en: "Hi {name}", uz: "Salom, {name}", ru: "Привет, {name}" },
  open_from_bot: {
    en: "Open this from the Telegram bot, not a regular browser.",
    uz: "Buni oddiy brauzerda emas, Telegram bot orqali oching.",
    ru: "Откройте это через Telegram-бота, а не в обычном браузере.",
  },
  cv_gate_hint: {
    en: "Upload your CV so I can search and score vacancies against it.",
    uz: "Vakansiyalarni qidirish va CV'ingizni ular bilan solishtirish uchun CV yuklang.",
    ru: "Загрузите резюме, чтобы я мог искать вакансии и сравнивать их с вашим резюме.",
  },
  cv_file_label: { en: "CV (PDF or DOCX)", uz: "CV (PDF yoki DOCX)", ru: "Резюме (PDF или DOCX)" },
  upload_cv_btn: { en: "📄 Upload CV", uz: "📄 CV yuklash", ru: "📄 Загрузить резюме" },
  title_screen_hint: {
    en: "What position are you looking for?", uz: "Qanday lavozimni qidiryapsiz?", ru: "Какую должность вы ищете?",
  },
  type_own: { en: "✍️ Type my own", uz: "✍️ O'zim kiritaman", ru: "✍️ Введу сам" },
  suggest_from_cv: { en: "🤖 Suggest from my CV", uz: "🤖 CV'imdan taklif qiling", ru: "🤖 Предложить по резюме" },
  job_title_label: { en: "Job title", uz: "Lavozim nomi", ru: "Название должности" },
  job_title_placeholder: { en: "e.g. Data Analyst", uz: "masalan: Data Analyst", ru: "например: Data Analyst" },
  next_btn: { en: "Next →", uz: "Keyingi →", ru: "Далее →" },
  suggest_different: {
    en: "🔄 Suggest different titles", uz: "🔄 Boshqa lavozimlarni taklif qilish", ru: "🔄 Предложить другие варианты",
  },
  searching_for_prefix: { en: "Searching for", uz: "Qidirilmoqda:", ru: "Ищу:" },
  change_link: { en: "← change", uz: "← o'zgartirish", ru: "← изменить" },
  location_label: { en: "Location", uz: "Joylashuv", ru: "Локация" },
  location_placeholder: {
    en: "e.g. Tashkent, Remote, Europe", uz: "masalan: Toshkent, Remote, Yevropa", ru: "например: Ташкент, Remote, Европа",
  },
  search_btn: { en: "🔍 Search", uz: "🔍 Qidirish", ru: "🔍 Искать" },
  applications_title: {
    en: "Your tracked applications", uz: "Kuzatilayotgan arizalaringiz", ru: "Ваши отслеживаемые заявки",
  },
  back_link: { en: "← back", uz: "← orqaga", ru: "← назад" },
  couldnt_load_profile: {
    en: "Couldn't load your profile.", uz: "Profilingizni yuklab bo'lmadi.", ru: "Не удалось загрузить ваш профиль.",
  },
  choose_file_first: {
    en: "Choose a PDF or DOCX file first.", uz: "Avval PDF yoki DOCX faylni tanlang.", ru: "Сначала выберите файл PDF или DOCX.",
  },
  reading_cv: { en: "📄 Reading your CV…", uz: "📄 CV'ingiz o'qilmoqda…", ru: "📄 Читаю ваше резюме…" },
  upload_failed: {
    en: "Upload failed, try again.", uz: "Yuklash amalga oshmadi, qaytadan urinib ko'ring.", ru: "Загрузка не удалась, попробуйте снова.",
  },
  analyzing_cv: { en: "🤖 Analyzing your CV…", uz: "🤖 CV'ingiz tahlil qilinmoqda…", ru: "🤖 Анализирую ваше резюме…" },
  suggestions_failed: {
    en: "Couldn't get suggestions, try again.", uz: "Takliflarni olib bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось получить варианты, попробуйте снова.",
  },
  enter_title_first: {
    en: "Enter a job title first.", uz: "Avval lavozim nomini kiriting.", ru: "Сначала введите название должности.",
  },
  status_applied: { en: "Applied", uz: "Yuborilgan", ru: "Подана" },
  status_phone_screen: { en: "Phone screen", uz: "Telefon suhbati", ru: "Телефонное интервью" },
  status_tech_interview: { en: "Tech interview", uz: "Texnik intervyu", ru: "Техническое интервью" },
  status_offer: { en: "Offer 🎉", uz: "Taklif 🎉", ru: "Оффер 🎉" },
  status_rejected: { en: "Rejected", uz: "Rad etilgan", ru: "Отказ" },
  status_ghosted: { en: "Ghosted", uz: "Javob kelmadi", ru: "Без ответа" },
  applications_load_failed: {
    en: "Couldn't load your applications.", uz: "Arizalaringizni yuklab bo'lmadi.", ru: "Не удалось загрузить ваши заявки.",
  },
  no_applications: {
    en: "Nothing tracked yet — like a vacancy and apply to see it here.",
    uz: "Hali hech narsa yo'q — vakansiyani yoqtiring va ariza bering, shunda u shu yerda ko'rinadi.",
    ru: "Пока пусто — отметьте вакансию как понравившуюся и подайте заявку, чтобы увидеть её здесь.",
  },
  no_applications_match_filter: {
    en: "No applications match this filter.", uz: "Bu filtrga mos ariza yo'q.", ru: "Нет заявок, соответствующих фильтру.",
  },
  filter_all: { en: "All statuses", uz: "Barcha holatlar", ru: "Все статусы" },
  sort_date: { en: "Newest first", uz: "Avval yangilari", ru: "Сначала новые" },
  sort_score: { en: "Highest match first", uz: "Avval eng mosi", ru: "Сначала с высоким совпадением" },
  status_label_prefix: { en: "Status:", uz: "Holat:", ru: "Статус:" },
  match_suffix: { en: "% match", uz: "% moslik", ru: "% совпадение" },
  view_posting: { en: "View posting →", uz: "E'lonni ko'rish →", ru: "Посмотреть вакансию →" },
  search_limit_session: {
    en: "You've used all 3 free vacancy searches for this session.",
    uz: "Ushbu sessiya uchun barcha 3 ta bepul vakansiya qidiruvidan foydalandingiz.",
    ru: "Вы использовали все 3 бесплатных поиска вакансий за эту сессию.",
  },
  searching_message: {
    en: "🔎 Searching for {title} in {location}… usually takes 15–30 seconds.",
    uz: "🔎 {title} bo'yicha {location} joyida qidirilmoqda… odatda 15–30 soniya vaqt oladi.",
    ru: "🔎 Ищу «{title}» в {location}… обычно занимает 15–30 секунд.",
  },
  search_failed: {
    en: "Search failed on our end. Please try again in a moment.",
    uz: "Qidiruv bizning tomonda amalga oshmadi. Birozdan keyin qayta urinib ko'ring.",
    ru: "Поиск не удался на нашей стороне. Попробуйте ещё раз через некоторое время.",
  },
  no_match_found: {
    en: "No matching posting found — try different criteria.",
    uz: "Mos e'lon topilmadi — boshqa mezonlar bilan urinib ko'ring.",
    ru: "Подходящая вакансия не найдена — попробуйте другие критерии.",
  },
  no_more_new_matches: {
    en: "No new postings found this time — here's what you already had.",
    uz: "Bu safar yangi e'lon topilmadi — avval topilganlar shu yerda.",
    ru: "На этот раз новых вакансий не найдено — вот то, что уже было найдено.",
  },
  like_this_one: { en: "Like this one?", uz: "Shu yoqdimi?", ru: "Нравится эта вакансия?" },
  yes_like_it: { en: "👍 Yes, I like it", uz: "👍 Ha, yoqdi", ru: "👍 Да, нравится" },
  search_again_btn: { en: "🔄 Search again", uz: "🔄 Qayta qidirish", ru: "🔄 Искать снова" },
  search_limit_title: {
    en: "You've used all 3 free vacancy searches for this session.",
    uz: "Ushbu sessiya uchun barcha 3 ta bepul vakansiya qidiruvidan foydalandingiz.",
    ru: "Вы использовали все 3 бесплатных поиска вакансий за эту сессию.",
  },
  search_cap_prompt: {
    en: "Want a deeper look? Analyze your CV against a specific job — get an ATS score, bullet-point fixes, and a step-by-step roadmap.",
    uz: "Chuqurroq tahlil kerakmi? CV'ingizni aniq bir ish e'loniga solishtiring — ATS bali, tuzatishlar va bosqichma-bosqich reja oling.",
    ru: "Хотите более глубокий анализ? Сравните резюме с конкретной вакансией — получите ATS-балл, исправления и пошаговый план.",
  },
  search_cap_analyze_btn: {
    en: "📊 Analyze my CV against a job", uz: "📊 CV'imni ish e'loniga solishtirish", ru: "📊 Сравнить резюме с вакансией",
  },
  carousel_prev: { en: "← Previous", uz: "← Oldingi", ru: "← Предыдущая" },
  carousel_next: { en: "Next →", uz: "Keyingi →", ru: "Следующая →" },
  how_proceed: { en: "How do you want to proceed?", uz: "Qanday davom etishni xohlaysiz?", ru: "Как хотите продолжить?" },
  apply_directly: { en: "✅ Apply directly", uz: "✅ To'g'ridan-to'g'ri ariza berish", ru: "✅ Подать заявку сразу" },
  check_cv_fit: { en: "📊 Check my CV fit", uz: "📊 CV moslikni tekshirish", ru: "📊 Проверить соответствие резюме" },
  saving: { en: "Saving…", uz: "Saqlanmoqda…", ru: "Сохраняю…" },
  apply_failed: {
    en: "Couldn't save your application, try again.", uz: "Arizangizni saqlab bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось сохранить заявку, попробуйте снова.",
  },
  checking_fit: {
    en: "📊 Comparing your CV to this vacancy…", uz: "📊 CV'ingiz ushbu vakansiya bilan solishtirilmoqda…", ru: "📊 Сравниваю ваше резюме с этой вакансией…",
  },
  scoring_failed: {
    en: "Couldn't score your CV, try again.", uz: "CV'ingizni baholab bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось оценить резюме, попробуйте снова.",
  },
  match_heading: { en: "{score}% Match", uz: "{score}% Moslik", ru: "{score}% Соответствие" },
  matched_label: { en: "Matched:", uz: "Mos keldi:", ru: "Совпало:" },
  missing_label: { en: "Missing:", uz: "Yetishmayapti:", ru: "Отсутствует:" },
  apply_anyway: { en: "✅ Apply anyway", uz: "✅ Baribir ariza berish", ru: "✅ Подать заявку в любом случае" },
  get_recommendations: { en: "📝 Get recommendations", uz: "📝 Tavsiyalar olish", ru: "📝 Получить рекомендации" },
  level_question: {
    en: "What's your level for this role?", uz: "Ushbu lavozim uchun darajangiz qanday?", ru: "Какой у вас уровень для этой роли?",
  },
  working_out_fixes: {
    en: "📝 Working out what to fix…", uz: "📝 Nimani tuzatish kerakligi aniqlanmoqda…", ru: "📝 Определяю, что нужно исправить…",
  },
  recommendations_failed: {
    en: "Couldn't get recommendations, try again.", uz: "Tavsiyalarni olib bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось получить рекомендации, попробуйте снова.",
  },
  issue_label: { en: "Issue:", uz: "Muammo:", ru: "Проблема:" },
  before_label: { en: "Before:", uz: "Oldin:", ru: "До:" },
  after_label: { en: "After:", uz: "Keyin:", ru: "После:" },
  ready_to_apply: {
    en: "Ready to apply, or want to improve your CV first?",
    uz: "Ariza berishga tayyormisiz, yoki avval CV'ingizni yaxshilamoqchimisiz?",
    ru: "Готовы подать заявку, или сначала хотите улучшить резюме?",
  },
  apply_now: { en: "✅ Apply now", uz: "✅ Hozir ariza berish", ru: "✅ Подать заявку сейчас" },
  improve_cv_btn: { en: "📄 Improve CV", uz: "📄 CV'ni yaxshilash", ru: "📄 Улучшить резюме" },
  upload_updated_cv: {
    en: "Upload your updated CV (PDF or DOCX).", uz: "Yangilangan CV'ingizni yuklang (PDF yoki DOCX).", ru: "Загрузите обновлённое резюме (PDF или DOCX).",
  },
  upload_improved_btn: {
    en: "📄 Upload improved CV", uz: "📄 Yaxshilangan CV'ni yuklash", ru: "📄 Загрузить улучшенное резюме",
  },
  reading_updated_cv: {
    en: "📄 Reading your updated CV…", uz: "📄 Yangilangan CV'ingiz o'qilmoqda…", ru: "📄 Читаю обновлённое резюме…",
  },
  improve_limit_reached: {
    en: "CV updated. You've reached the improve limit for this vacancy — ready to apply.",
    uz: "CV yangilandi. Ushbu vakansiya uchun yaxshilash chegarasiga yetdingiz — ariza berishga tayyor.",
    ru: "Резюме обновлено. Вы достигли лимита улучшений для этой вакансии — можно подавать заявку.",
  },
  improve_choice: {
    en: "CV updated. Apply now, or check your new match % first?",
    uz: "CV yangilandi. Hozir ariza berasizmi, yoki avval yangi moslik foizini tekshirasizmi?",
    ru: "Резюме обновлено. Подать заявку сейчас или сначала проверить новый процент соответствия?",
  },
  check_match_again: { en: "📊 Check match again", uz: "📊 Moslikni qayta tekshirish", ru: "📊 Проверить соответствие снова" },
  saved_confirmation: {
    en: "✅ Saved to your tracked applications.", uz: "✅ Kuzatilayotgan arizalaringizga saqlandi.", ru: "✅ Сохранено в отслеживаемых заявках.",
  },
  view_my_applications: { en: "📋 View my applications", uz: "📋 Arizalarimni ko'rish", ru: "📋 Посмотреть мои заявки" },
  update_status_prompt: { en: "Update status:", uz: "Holatni yangilash:", ru: "Обновить статус:" },
  delete_application_btn: { en: "🗑 Delete application", uz: "🗑 Arizani o'chirish", ru: "🗑 Удалить заявку" },
  status_updated: { en: "✅ Status updated.", uz: "✅ Holat yangilandi.", ru: "✅ Статус обновлён." },
  status_update_failed: {
    en: "Couldn't update status, try again.", uz: "Holatni yangilab bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось обновить статус, попробуйте снова.",
  },
  delete_confirm: {
    en: "Delete this application? This can't be undone.",
    uz: "Ushbu arizani o'chirasizmi? Buni qaytarib bo'lmaydi.",
    ru: "Удалить эту заявку? Это действие нельзя отменить.",
  },
  delete_confirm_yes: { en: "Yes, delete", uz: "Ha, o'chirish", ru: "Да, удалить" },
  delete_confirm_no: { en: "Cancel", uz: "Bekor qilish", ru: "Отмена" },
  delete_failed: {
    en: "Couldn't delete, try again.", uz: "O'chirib bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось удалить, попробуйте снова.",
  },
  err_timeout: {
    en: "That took too long and timed out — please try again.",
    uz: "Bu juda uzoq davom etdi va vaqt tugadi — qaytadan urinib ko'ring.",
    ru: "Это заняло слишком много времени — попробуйте снова.",
  },
  err_network: {
    en: "Couldn't connect — check your internet connection and try again.",
    uz: "Ulanib bo'lmadi — internet aloqangizni tekshiring va qaytadan urinib ko'ring.",
    ru: "Не удалось подключиться — проверьте интернет-соединение и попробуйте снова.",
  },
  err_session_expired: {
    en: "Your session expired — close this and reopen it from the bot.",
    uz: "Sessiya muddati tugadi — buni yoping va botdan qaytadan oching.",
    ru: "Сессия истекла — закройте это и откройте заново через бота.",
  },
  err_generic: {
    en: "Something went wrong. Please try again.", uz: "Nimadir xato ketdi. Qaytadan urinib ko'ring.", ru: "Что-то пошло не так. Попробуйте снова.",
  },
  home_hint: {
    en: "Please choose an option:", uz: "Kerakli bo'limni tanlang:", ru: "Пожалуйста, выберите один из вариантов:",
  },
  home_analyze_option: {
    en: "📊 Analyze my CV against a job", uz: "📊 CV'imni ish e'loniga solishtirish", ru: "📊 Сравнить резюме с вакансией",
  },
  home_analyze_hint: {
    en: "Get an ATS score, bullet-point fixes, and a step-by-step roadmap.",
    uz: "ATS bali, tuzatishlar va bosqichma-bosqich reja oling.",
    ru: "Получите ATS-балл, исправления и пошаговый план.",
  },
  home_vacancy_option: {
    en: "🔍 Find & track vacancies", uz: "🔍 Vakansiya topish va kuzatish", ru: "🔍 Найти и отслеживать вакансии",
  },
  home_vacancy_hint: {
    en: "Search live postings and keep track of where you've applied.",
    uz: "Joriy e'lonlarni qidiring va qayerga ariza berganingizni kuzating.",
    ru: "Ищите актуальные вакансии и отслеживайте, куда вы откликнулись.",
  },
  analysis_title: {
    en: "CV vs Job Analysis", uz: "CV va ish e'loni tahlili", ru: "Анализ резюме и вакансии",
  },
  jd_label: {
    en: "Paste the job description, or a link to it", uz: "Ish e'loni matnini yoki havolasini joylashtiring", ru: "Вставьте текст вакансии или ссылку на неё",
  },
  jd_placeholder: {
    en: "Paste the full job posting text, or a link to it…",
    uz: "To'liq ish e'loni matnini yoki havolasini shu yerga joylashtiring…",
    ru: "Вставьте сюда полный текст вакансии или ссылку на неё…",
  },
  analyze_btn: { en: "🤖 Analyze", uz: "🤖 Tahlil qilish", ru: "🤖 Анализировать" },
  jd_too_short_web: {
    en: "Paste a fuller job description (at least 100 characters), or a link to the posting.",
    uz: "To'liqroq ish e'loni matnini (kamida 100 belgi) yoki e'lon havolasini joylashtiring.",
    ru: "Вставьте более полный текст вакансии (не менее 100 символов) или ссылку на вакансию.",
  },
  analyzing_message_web: {
    en: "🤖 Analyzing your CV against this job… usually takes 15–30 seconds.",
    uz: "🤖 CV'ingiz ushbu ish e'loni bilan tahlil qilinmoqda… odatda 15–30 soniya vaqt oladi.",
    ru: "🤖 Анализирую ваше резюме по этой вакансии… обычно занимает 15–30 секунд.",
  },
  analyzing_link_message_web: {
    en: "🔗 Reading the job posting from your link, then analyzing… usually takes 15–30 seconds.",
    uz: "🔗 Havoladagi ish e'loni o'qilmoqda, so'ng tahlil qilinadi… odatda 15–30 soniya vaqt oladi.",
    ru: "🔗 Читаю вакансию по вашей ссылке, затем анализирую… обычно занимает 15–30 секунд.",
  },
  analysis_failed_web: {
    en: "Analysis failed on our end. Please try again in a moment.",
    uz: "Tahlil bizning tomonda amalga oshmadi. Birozdan keyin qayta urinib ko'ring.",
    ru: "Анализ не удался на нашей стороне. Попробуйте ещё раз через некоторое время.",
  },
  ats_heading: { en: "ATS Score", uz: "ATS Bali", ru: "ATS-балл" },
  xyz_heading: { en: "Bullet Point Check", uz: "Band tekshiruvi", ru: "Проверка формулировок" },
  xyz_passing_label: { en: "✅ Passing:", uz: "✅ O'tgan:", ru: "✅ Хорошо:" },
  xyz_failing_label: { en: "❌ Needs work:", uz: "❌ Yaxshilash kerak:", ru: "❌ Нужна доработка:" },
  xyz_rewrites_label: { en: "Suggested rewrites:", uz: "Tavsiya etilgan tahrirlar:", ru: "Предлагаемые правки:" },
  tools_heading: { en: "Tool Radar", uz: "Vositalar radari", ru: "Радар инструментов" },
  tool_strong: { en: "Strong", uz: "Kuchli", ru: "Сильно" },
  tool_mentioned: { en: "Mentioned", uz: "Tilga olingan", ru: "Упомянуто" },
  tool_not_found: { en: "Not found", uz: "Topilmadi", ru: "Не найдено" },
  level_heading: { en: "Your Level", uz: "Sizning darajangiz", ru: "Ваш уровень" },
  get_roadmap_btn: { en: "🗺 Get My Roadmap", uz: "🗺 Rejamni olish", ru: "🗺 Получить план" },
  roadmap_continue_btn: { en: "Continue →", uz: "Davom etish →", ru: "Продолжить →" },
  roadmap_failed_web: {
    en: "Couldn't build this section, try again.", uz: "Bu bo'limni tayyorlab bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось подготовить этот раздел, попробуйте снова.",
  },
  roadmap_done: {
    en: "✅ That's the end of your roadmap. Good luck!", uz: "✅ Rejangiz shu bilan tugaydi. Omad tilaymiz!", ru: "✅ На этом ваш план завершён. Удачи!",
  },
  analysis_limit_reached: {
    en: "🚦 You've used all your free checks.", uz: "🚦 Siz barcha bepul tekshiruvlaringizdan foydalandingiz.", ru: "🚦 Вы использовали все бесплатные проверки.",
  },
  buy_checks_intro: {
    en: "Buy more — {price} UZS per check. Choose how many:",
    uz: "Ko'proq sotib oling — har biri {price} so'm. Nechtasini xohlaysiz?",
    ru: "Купите ещё — по {price} сум за проверку. Выберите количество:",
  },
  buy_custom_btn: { en: "🔢 Custom amount", uz: "🔢 Boshqa miqdor", ru: "🔢 Другое количество" },
  buy_custom_prompt: {
    en: "How many checks? Enter a number from 1 to 100.",
    uz: "Nechta tekshiruv? 1 dan 100 gacha son kiriting.",
    ru: "Сколько проверок? Введите число от 1 до 100.",
  },
  buy_custom_confirm: { en: "Confirm", uz: "Tasdiqlash", ru: "Подтвердить" },
  buy_custom_invalid: {
    en: "Enter a whole number from 1 to 100.", uz: "1 dan 100 gacha butun son kiriting.", ru: "Введите целое число от 1 до 100.",
  },
  checkout_opening: { en: "Opening checkout…", uz: "To'lov ochilmoqda…", ru: "Открываю оплату…" },
  checkout_failed: {
    en: "Couldn't start checkout, try again.", uz: "To'lovni boshlab bo'lmadi, qaytadan urinib ko'ring.", ru: "Не удалось начать оплату, попробуйте снова.",
  },
  checks_word: { en: "checks", uz: "ta tekshiruv", ru: "проверок" },
  check_word_one: { en: "check", uz: "ta tekshiruv", ru: "проверка" },
  welcome_body: {
    en: "👋 Welcome to AcceptedAI. I help you get accepted into your dream job — analyze your CV against a job description, or find and track vacancies.",
    uz: "👋 AcceptedAI'ga xush kelibsiz. Men sizga orzuingizdagi ishga qabul qilinishda yordam beraman — CV'ingizni ish e'loniga solishtiring yoki vakansiyalarni toping va kuzating.",
    ru: "👋 Добро пожаловать в AcceptedAI. Я помогу вам получить работу мечты — сравните резюме с вакансией или найдите и отслеживайте вакансии.",
  },
  welcome_continue_btn: { en: "Get started →", uz: "Boshlash →", ru: "Начать →" },
  profile_title: { en: "Profile", uz: "Profil", ru: "Профиль" },
  profile_checks_line: {
    en: "You have {remaining} of {quota} free checks left.",
    uz: "Sizda {quota} tadan {remaining} ta bepul tekshiruv qoldi.",
    ru: "У вас осталось {remaining} из {quota} бесплатных проверок.",
  },
  profile_buy_more_btn: { en: "💳 Buy more checks", uz: "💳 Ko'proq tekshiruv sotib olish", ru: "💳 Купить ещё проверок" },
  nav_checks_badge: { en: "🎫 {remaining}/{quota}", uz: "🎫 {remaining}/{quota}", ru: "🎫 {remaining}/{quota}" },
  post_roadmap_no_checks: {
    en: "You're out of free checks. Buy more to analyze another job:",
    uz: "Bepul tekshiruvlaringiz tugadi. Boshqa ish e'lonini tahlil qilish uchun ko'proq sotib oling:",
    ru: "У вас закончились бесплатные проверки. Купите ещё, чтобы проанализировать другую вакансию:",
  },
  post_roadmap_checks_left: {
    en: "You have {remaining}/{quota} free checks left.",
    uz: "Sizda {remaining}/{quota} ta bepul tekshiruv qoldi.",
    ru: "У вас осталось {remaining}/{quota} бесплатных проверок.",
  },
  analyze_another_btn: {
    en: "📊 Analyze another job", uz: "📊 Boshqa ish e'lonini tahlil qilish", ru: "📊 Проанализировать другую вакансию",
  },
};

let currentLang = "en";

function t(key, vars) {
  const entry = I18N[key];
  let text = (entry && (entry[currentLang] || entry.en)) || key;
  if (vars) {
    for (const k in vars) text = text.replace(`{${k}}`, vars[k]);
  }
  return text;
}

function applyStaticTranslations() {
  document.getElementById("nav-applications").textContent = t("nav_applications");
  document.getElementById("cv-gate-hint").textContent = t("cv_gate_hint");
  document.getElementById("cv-file-label").textContent = t("cv_file_label");
  document.getElementById("upload_btn").textContent = t("upload_cv_btn");
  document.getElementById("home-hint").textContent = t("home_hint");
  document.getElementById("home-analyze-option").textContent = t("home_analyze_option");
  document.getElementById("home-analyze-hint").textContent = t("home_analyze_hint");
  document.getElementById("home-vacancy-option").textContent = t("home_vacancy_option");
  document.getElementById("home-vacancy-hint").textContent = t("home_vacancy_hint");
  document.getElementById("analysis-title").textContent = t("analysis_title");
  document.getElementById("btn-analysis-back").textContent = t("back_link");
  document.getElementById("jd-label").textContent = t("jd_label");
  document.getElementById("jd_text").placeholder = t("jd_placeholder");
  document.getElementById("analyze_btn").textContent = t("analyze_btn");
  document.getElementById("btn-title-back").textContent = t("back_link");
  document.getElementById("title-screen-hint").textContent = t("title_screen_hint");
  document.getElementById("btn-type-own").textContent = t("type_own");
  document.getElementById("btn-suggest-cv").textContent = t("suggest_from_cv");
  document.getElementById("manual-title-label").textContent = t("job_title_label");
  document.getElementById("manual_title").placeholder = t("job_title_placeholder");
  document.getElementById("btn-next-title").textContent = t("next_btn");
  document.getElementById("btn-suggest-again").textContent = t("suggest_different");
  document.getElementById("searching-for-label").firstChild.textContent = t("searching_for_prefix") + " ";
  document.getElementById("btn-change-title").textContent = t("change_link");
  document.getElementById("location-label").textContent = t("location_label");
  document.getElementById("location").placeholder = t("location_placeholder");
  document.getElementById("search_btn").textContent = t("search_btn");
  document.getElementById("applications-title").textContent = t("applications_title");
  document.getElementById("btn-applications-back").textContent = t("back_link");
  document.getElementById("btn-cv-gate-back").textContent = t("back_link");
  document.getElementById("welcome-body").textContent = t("welcome_body");
  document.getElementById("welcome-continue-btn").textContent = t("welcome_continue_btn");
  document.getElementById("profile-title").textContent = t("profile_title");
  document.getElementById("btn-profile-back").textContent = t("back_link");

  const filterEl = document.getElementById("applications-filter");
  filterEl.innerHTML = ['all', 'applied', 'phone_screen', 'tech_interview', 'offer', 'rejected', 'ghosted']
    .map(s => `<option value="${s}">${escapeHtml(s === 'all' ? t('filter_all') : statusLabel(s))}</option>`).join("");
  const sortEl = document.getElementById("applications-sort");
  sortEl.innerHTML = `<option value="date">${escapeHtml(t('sort_date'))}</option><option value="score">${escapeHtml(t('sort_score'))}</option>`;
}

// ── app ──────────────────────────────────────────────────────────────
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const state = {
  jobTitle: "", seenCompanies: [], searchCount: 0,
  vacancies: [], vacancyIndex: -1, improveCount: 0,
  jd: "", analysisLevel: "", analysisRemaining: null, analysisQuota: null,
  hasCv: false, postUploadDestination: null,
};
const MAX_SEARCHES = 3;
const MAX_IMPROVES = 2;
const CHECK_QUANTITY_PRESETS = [1, 5, 10, 20, 50];
const MIN_CHECKS_PURCHASE = 1;
const MAX_CHECKS_PURCHASE = 100;

function showScreen(id) {
  for (const s of ["loading-gate", "welcome-screen", "cv-gate", "home-screen", "profile-screen", "analysis-screen", "title-screen", "search-screen", "applications-screen"]) {
    document.getElementById(s).hidden = (s !== id);
  }
}

function goHome() { showScreen("home-screen"); }

function goToVacancySearch() {
  if (!state.hasCv) {
    state.postUploadDestination = "vacancy";
    showScreen("cv-gate");
    return;
  }
  showScreen("title-screen");
}

function goToAnalysis() {
  if (!state.hasCv) {
    state.postUploadDestination = "analysis";
    showScreen("cv-gate");
    return;
  }
  document.getElementById("jd-input-box").hidden = false;
  document.getElementById("analysis-result").innerHTML = "";
  showScreen("analysis-screen");
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  });
}

function updateChecksHeader(remaining, quota) {
  const badge = document.getElementById("nav-checks");
  badge.textContent = t("nav_checks_badge", { remaining, quota });
  badge.hidden = false;
}

async function refreshChecksHeader() {
  try {
    const q = await callApi("/api/quota-status", {});
    updateChecksHeader(q.remaining, q.quota);
  } catch (err) {
    console.error("Couldn't load quota status for header:", err);
  }
}

async function checkCVAndRoute() {
  if (!tg || !tg.initData) {
    document.getElementById("loading-gate").innerHTML =
      `<div class="error">${escapeHtml(t("open_from_bot"))}</div>`;
    return;
  }
  try {
    const res = await fetch("/api/cv-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ init_data: tg.initData }),
    });
    if (!res.ok) throw new Error("status check failed");
    const data = await res.json();
    currentLang = data.lang || "en";
    applyStaticTranslations();
    state.hasCv = data.has_cv;

    const userInfo = tg.initDataUnsafe?.user;
    if (userInfo) {
      document.getElementById("greeting").textContent = t("greeting", { name: userInfo.first_name });
    }

    showScreen(data.has_cv ? "home-screen" : "welcome-screen");
    document.getElementById("nav-applications").hidden = false;
    refreshChecksHeader();
  } catch (err) {
    console.error("CV status check failed:", err);
    document.getElementById("loading-gate").innerHTML =
      `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("couldnt_load_profile")))}</div>`;
  }
}
checkCVAndRoute();

async function showProfile() {
  showScreen("profile-screen");
  const contentEl = document.getElementById("profile-content");
  contentEl.innerHTML = `<div class="hint">…</div>`;
  try {
    const q = await callApi("/api/quota-status", {});
    updateChecksHeader(q.remaining, q.quota);
    contentEl.innerHTML = `
      <div class="card">
        <div>${escapeHtml(t("profile_checks_line", { remaining: q.remaining, quota: q.quota }))}</div>
      </div>
    `;
    if (q.remaining <= 0) {
      const buyBox = document.createElement("div");
      buyBox.style.marginTop = "12px";
      contentEl.appendChild(buyBox);
      await renderBuyChecks(buyBox);
    } else {
      const btn = document.createElement("button");
      btn.className = "secondary";
      btn.textContent = t("profile_buy_more_btn");
      btn.onclick = async () => {
        const buyBox = document.createElement("div");
        contentEl.appendChild(buyBox);
        await renderBuyChecks(buyBox);
      };
      contentEl.appendChild(btn);
    }
  } catch (err) {
    console.error("Couldn't load profile:", err);
    contentEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("couldnt_load_profile")))}</div>`;
  }
}

async function uploadCV() {
  const fileInput = document.getElementById("cv_file");
  const resultEl = document.getElementById("upload_result");
  const btn = document.getElementById("upload_btn");
  const file = fileInput.files[0];

  if (!file) {
    resultEl.innerHTML = `<div class="error">${escapeHtml(t("choose_file_first"))}</div>`;
    return;
  }

  btn.disabled = true;
  resultEl.innerHTML = `<div class="hint">${escapeHtml(t("reading_cv"))}</div>`;

  const formData = new FormData();
  formData.append("init_data", tg.initData);
  formData.append("file", file);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);
  try {
    const res = await fetch("/api/upload-cv", { method: "POST", body: formData, signal: controller.signal });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      console.error("Upload failed:", res.status, body);
      const err = new Error(body.detail || "");
      if (res.status === 401) err.sessionExpired = true;
      throw err;
    }
    state.hasCv = true;
    if (state.postUploadDestination === "analysis") {
      state.postUploadDestination = null;
      document.getElementById("jd-input-box").hidden = false;
      document.getElementById("analysis-result").innerHTML = "";
      showScreen("analysis-screen");
    } else if (state.postUploadDestination === "vacancy") {
      state.postUploadDestination = null;
      showScreen("title-screen");
    } else {
      showScreen("home-screen");
    }
  } catch (err) {
    console.error("CV upload failed:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("upload_failed")))}</div>`;
  } finally {
    clearTimeout(timeout);
    btn.disabled = false;
  }
}

function showManualTitle() {
  document.getElementById("suggested-titles-box").hidden = true;
  document.getElementById("manual-title-box").hidden = false;
}

async function suggestTitles() {
  document.getElementById("manual-title-box").hidden = true;
  const box = document.getElementById("suggested-titles-box");
  const chipsEl = document.getElementById("title-chips");
  const errEl = document.getElementById("title-error");
  box.hidden = false;
  errEl.innerHTML = "";
  chipsEl.innerHTML = `<div class="hint">${escapeHtml(t("analyzing_cv"))}</div>`;

  try {
    const data = await callApi("/api/suggest-titles", {});
    chipsEl.innerHTML = "";
    for (const title of data.titles) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = title;
      chip.onclick = () => pickTitle(title);
      chipsEl.appendChild(chip);
    }
  } catch (err) {
    console.error("Suggest titles failed:", err);
    chipsEl.innerHTML = "";
    errEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("suggestions_failed")))}</div>`;
  }
}

function pickTitle(title) {
  if (!title) {
    document.getElementById("title-error").innerHTML = `<div class="error">${escapeHtml(t("enter_title_first"))}</div>`;
    return;
  }
  state.jobTitle = title;
  state.seenCompanies = [];
  state.vacancies = [];
  state.vacancyIndex = -1;
  state.improveCount = 0;
  document.getElementById("chosen-title-label").textContent = title;
  document.getElementById("result").innerHTML = "";
  showScreen("search-screen");
}

function backToTitleScreen() {
  showScreen("title-screen");
}

function statusLabel(status) {
  const key = "status_" + status;
  return I18N[key] ? t(key) : status;
}

// ── Applications ─────────────────────────────────────────────────────
let allApplications = [];

async function showApplications() {
  showScreen("applications-screen");
  document.getElementById("application-detail").hidden = true;
  document.getElementById("applications-list").hidden = false;
  document.getElementById("applications-controls").hidden = false;
  document.getElementById("btn-applications-back").hidden = false;
  const listEl = document.getElementById("applications-list");
  listEl.innerHTML = '<div class="hint">…</div>';

  try {
    const data = await callApi("/api/applications", {});
    allApplications = data.applications || [];
    renderApplications();
  } catch (err) {
    console.error("Loading applications failed:", err);
    listEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("applications_load_failed")))}</div>`;
  }
}

function renderApplications() {
  const listEl = document.getElementById("applications-list");
  if (allApplications.length === 0) {
    listEl.innerHTML = `<div class="hint">${escapeHtml(t("no_applications"))}</div>`;
    return;
  }

  const filterVal = document.getElementById("applications-filter").value;
  const sortVal = document.getElementById("applications-sort").value;

  let apps = allApplications.slice();
  if (filterVal && filterVal !== "all") apps = apps.filter(a => a.status === filterVal);
  if (sortVal === "score") {
    apps.sort((a, b) => (b.match_score ?? -1) - (a.match_score ?? -1));
  } else {
    apps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }

  if (apps.length === 0) {
    listEl.innerHTML = `<div class="hint">${escapeHtml(t("no_applications_match_filter"))}</div>`;
    return;
  }

  listEl.innerHTML = apps.map(a => {
    const date = new Date(a.created_at).toLocaleDateString();
    const status = statusLabel(a.status);
    const scoreLine = (a.match_score !== null && a.match_score !== undefined)
      ? `<div>${a.match_score}${escapeHtml(t("match_suffix"))}</div>` : "";
    return `
      <div class="card clickable" style="margin-bottom:8px;" onclick="openApplicationDetail(${a.id})">
        <h3>${escapeHtml(a.title)}</h3>
        <div class="company">${escapeHtml(a.company)}${a.location ? " · " + escapeHtml(a.location) : ""}</div>
        ${scoreLine}
        <div>${escapeHtml(t("status_label_prefix"))} <b>${escapeHtml(status)}</b> · ${escapeHtml(date)}</div>
      </div>
    `;
  }).join("");
}

function openApplicationDetail(id) {
  const app = allApplications.find(a => a.id === id);
  if (!app) return;
  document.getElementById("applications-list").hidden = true;
  document.getElementById("applications-controls").hidden = true;
  document.getElementById("btn-applications-back").hidden = true;
  const detailEl = document.getElementById("application-detail");
  detailEl.hidden = false;

  const statusOrder = ["applied", "phone_screen", "tech_interview", "offer", "rejected", "ghosted"];
  detailEl.innerHTML = `
    <button class="back-btn" onclick="closeApplicationDetail()">${escapeHtml(t("back_link"))}</button>
    <div class="card" style="margin-top:12px;">
      <h3>${escapeHtml(app.title)}</h3>
      <div class="company">${escapeHtml(app.company)}${app.location ? " · " + escapeHtml(app.location) : ""}</div>
      ${(app.match_score !== null && app.match_score !== undefined) ? `<div>${app.match_score}${escapeHtml(t("match_suffix"))}</div>` : ""}
      ${app.url ? `<a href="${app.url}" target="_blank">${escapeHtml(t("view_posting"))}</a>` : ""}
    </div>
    <div class="prompt-block">${escapeHtml(t("update_status_prompt"))}</div>
    <div id="status-buttons">
      ${statusOrder.map(s => `
        <button class="${s === app.status ? '' : 'secondary'}" style="margin-top:8px;" onclick="setApplicationStatus(${app.id}, '${s}')">${escapeHtml(statusLabel(s))}</button>
      `).join("")}
    </div>
    <button class="danger" onclick="confirmDeleteApplication(${app.id})">${escapeHtml(t("delete_application_btn"))}</button>
    <div id="detail-action-result"></div>
  `;
  scrollToBottom();
}

function closeApplicationDetail() {
  document.getElementById("application-detail").hidden = true;
  document.getElementById("applications-list").hidden = false;
  document.getElementById("applications-controls").hidden = false;
  document.getElementById("btn-applications-back").hidden = false;
}

async function setApplicationStatus(id, status) {
  const resultEl = document.getElementById("detail-action-result");
  resultEl.innerHTML = `<div class="hint">${escapeHtml(t("saving"))}</div>`;
  try {
    await callApi("/api/applications/update-status", { application_id: id, status });
    const app = allApplications.find(a => a.id === id);
    if (app) app.status = status;
    openApplicationDetail(id);
    document.getElementById("detail-action-result").innerHTML = `<div class="hint">${escapeHtml(t("status_updated"))}</div>`;
  } catch (err) {
    console.error("Status update failed:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("status_update_failed")))}</div>`;
  }
}

function confirmDeleteApplication(id) {
  const resultEl = document.getElementById("detail-action-result");
  resultEl.innerHTML = `
    <div class="prompt-block">${escapeHtml(t("delete_confirm"))}</div>
    <div class="row">
      <button class="danger" onclick="deleteApplicationNow(${id})">${escapeHtml(t("delete_confirm_yes"))}</button>
      <button class="secondary" onclick="document.getElementById('detail-action-result').innerHTML=''">${escapeHtml(t("delete_confirm_no"))}</button>
    </div>
  `;
  scrollToBottom();
}

async function deleteApplicationNow(id) {
  const resultEl = document.getElementById("detail-action-result");
  resultEl.innerHTML = `<div class="hint">${escapeHtml(t("saving"))}</div>`;
  try {
    await callApi("/api/applications/delete", { application_id: id });
    allApplications = allApplications.filter(a => a.id !== id);
    closeApplicationDetail();
    renderApplications();
  } catch (err) {
    console.error("Delete failed:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("delete_failed")))}</div>`;
  }
}

// ── Search / vacancy carousel ────────────────────────────────────────
async function search() {
  const location = document.getElementById("location").value.trim() || "Any";
  const resultEl = document.getElementById("result");
  const btn = document.getElementById("search_btn");

  if (!tg || !tg.initData) {
    resultEl.innerHTML = `<div class="error">${escapeHtml(t("open_from_bot"))}</div>`;
    return;
  }
  if (state.searchCount >= MAX_SEARCHES) {
    resultEl.innerHTML = `<div class="hint">${escapeHtml(t("search_limit_session"))}</div>${searchCapCta()}`;
    return;
  }

  btn.disabled = true;
  resultEl.innerHTML = `<div class="hint">${escapeHtml(t("searching_message", { title: state.jobTitle, location: location }))}</div>`;

  try {
    const data = await callApi("/api/search", {
      job_title: state.jobTitle,
      location: location,
      seen_companies: state.seenCompanies,
    });
    state.searchCount += 1;
    const newVacancies = data.vacancies || [];

    if (newVacancies.length === 0 && state.vacancies.length === 0) {
      resultEl.innerHTML = `<div class="hint">${escapeHtml(t("no_match_found"))}</div>`;
      return;
    }

    if (newVacancies.length > 0) {
      const startIndex = state.vacancies.length;
      state.vacancies.push(...newVacancies);
      for (const v of newVacancies) state.seenCompanies.push(v.company);
      state.vacancyIndex = startIndex;
    } else {
      resultEl.innerHTML = `<div class="hint">${escapeHtml(t("no_more_new_matches"))}</div>`;
    }
    state.improveCount = 0;
    renderVacancyCard();
  } catch (err) {
    console.error("Search error:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("search_failed")))}</div>`;
  } finally {
    btn.disabled = false;
  }
}

function currentVacancy() {
  return state.vacancies[state.vacancyIndex];
}

function showVacancy(index) {
  if (index < 0 || index >= state.vacancies.length) return;
  state.vacancyIndex = index;
  state.improveCount = 0;
  renderVacancyCard();
}

function renderVacancyCard() {
  const resultEl = document.getElementById("result");
  const total = state.vacancies.length;
  if (total === 0) {
    resultEl.innerHTML = `<div class="hint">${escapeHtml(t("no_match_found"))}</div>`;
    return;
  }
  const v = currentVacancy();
  const canSearchAgain = state.searchCount < MAX_SEARCHES;
  const canPrev = state.vacancyIndex > 0;
  const canNext = state.vacancyIndex < total - 1;

  resultEl.innerHTML = `
    <div class="card">
      <h3>${escapeHtml(v.title)}</h3>
      <div class="company">${escapeHtml(v.company)} · ${escapeHtml(v.location)}</div>
      <p>${escapeHtml(v.summary)}</p>
      <a href="${v.url}" target="_blank">${escapeHtml(t("view_posting"))}</a>
    </div>
    ${total > 1 ? `
      <div class="nav-row">
        <button class="secondary" onclick="showVacancy(${state.vacancyIndex - 1})" ${canPrev ? '' : 'disabled'}>${escapeHtml(t("carousel_prev"))}</button>
        <span class="nav-counter">${state.vacancyIndex + 1} / ${total}</span>
        <button class="secondary" onclick="showVacancy(${state.vacancyIndex + 1})" ${canNext ? '' : 'disabled'}>${escapeHtml(t("carousel_next"))}</button>
      </div>
    ` : ''}
    <div class="prompt-block">${escapeHtml(t("like_this_one"))}</div>
    <div class="row">
      <button onclick="likeVacancy()">${escapeHtml(t("yes_like_it"))}</button>
      ${canSearchAgain ? `<button class="secondary" onclick="search()">${escapeHtml(t("search_again_btn"))}</button>` : ''}
    </div>
    ${!canSearchAgain ? `<div class="hint" style="margin-top:8px;">${escapeHtml(t("search_limit_title"))}</div>${searchCapCta()}` : ''}
    <div id="action-area"></div>
  `;
  scrollToBottom();
}

function searchCapCta() {
  return `
    <div class="prompt-block">${escapeHtml(t("search_cap_prompt"))}</div>
    <button onclick="goToAnalysis()">${escapeHtml(t("search_cap_analyze_btn"))}</button>
  `;
}

function actionArea() {
  return document.getElementById("action-area");
}

function likeVacancy() {
  state.improveCount = 0;
  actionArea().innerHTML = `
    <div class="prompt-block">${escapeHtml(t("how_proceed"))}</div>
    <div class="row">
      <button onclick="applyDirectly()">${escapeHtml(t("apply_directly"))}</button>
      <button class="secondary" onclick="checkFit()">${escapeHtml(t("check_cv_fit"))}</button>
    </div>
  `;
  scrollToBottom();
}

async function callApi(path, body, btn) {
  if (btn) btn.disabled = true;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);
  try {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ init_data: tg.initData, ...body }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      console.error("API call failed:", path, res.status, errBody);
      const err = new Error(errBody.detail || "");
      if (res.status === 401) err.sessionExpired = true;
      throw err;
    }
    return await res.json();
  } finally {
    clearTimeout(timeout);
    if (btn) btn.disabled = false;
  }
}

// Maps any thrown error into a specific, non-technical message. Never
// shows raw server/network text to the user (that goes to console only).
// Note: `fallback` is already-localized text from the call site; only
// backend `detail` strings (err.message) remain English-only for now.
function friendlyError(err, fallback) {
  if (err && err.name === "AbortError") return t("err_timeout");
  if (err instanceof TypeError) return t("err_network");
  if (err && err.sessionExpired) return t("err_session_expired");
  if (err && typeof err.message === "string" && err.message.trim()) return err.message;
  return fallback || t("err_generic");
}

async function applyDirectly() {
  actionArea().innerHTML = `<div class="hint">${escapeHtml(t("saving"))}</div>`;
  try {
    await callApi("/api/apply", { vacancy: currentVacancy(), score: null });
    renderSaved();
  } catch (err) {
    console.error("Apply failed:", err);
    actionArea().innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("apply_failed")))}</div>`;
  }
  scrollToBottom();
}

async function checkFit() {
  actionArea().innerHTML = `<div class="hint">${escapeHtml(t("checking_fit"))}</div>`;
  try {
    const score = await callApi("/api/score-vacancy", { vacancy: currentVacancy() });
    state.lastScore = score;
    renderScoreResult(score);
  } catch (err) {
    console.error("Scoring failed:", err);
    actionArea().innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("scoring_failed")))}</div>`;
  }
  scrollToBottom();
}

function renderScoreResult(score) {
  const matched = (score.matched || []).join(", ") || "—";
  const missing = (score.missing || []).join(", ") || "—";
  actionArea().innerHTML = `
    <div class="card" style="margin-top:16px;">
      <h3>${escapeHtml(t("match_heading", { score: score.score }))}</h3>
      <p>${escapeHtml(score.verdict || "")}</p>
      <div>✅ <b>${escapeHtml(t("matched_label"))}</b> ${escapeHtml(matched)}</div>
      <div>❌ <b>${escapeHtml(t("missing_label"))}</b> ${escapeHtml(missing)}</div>
    </div>
    <div class="row">
      <button onclick="applyDirectly()">${escapeHtml(t("apply_anyway"))}</button>
      ${state.improveCount < MAX_IMPROVES ? `<button class="secondary" onclick="showLevelPicker()">${escapeHtml(t("get_recommendations"))}</button>` : ''}
    </div>
  `;
  scrollToBottom();
}

function showLevelPicker() {
  actionArea().insertAdjacentHTML("beforeend", `
    <div class="prompt-block">${escapeHtml(t("level_question"))}</div>
    <div class="row">
      <button onclick="getRecommendations('Junior')">Junior</button>
      <button onclick="getRecommendations('Mid')">Mid</button>
      <button onclick="getRecommendations('Senior')">Senior</button>
    </div>
  `);
  scrollToBottom();
}

async function getRecommendations(level) {
  actionArea().innerHTML = `<div class="hint">${escapeHtml(t("working_out_fixes"))}</div>`;
  try {
    const data = await callApi("/api/cv-recommendations", { vacancy: currentVacancy(), level });
    renderRecommendations(data.fixes);
  } catch (err) {
    console.error("Recommendations failed:", err);
    actionArea().innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("recommendations_failed")))}</div>`;
  }
  scrollToBottom();
}

function renderRecommendations(fixes) {
  const cards = (fixes || []).map(f => `
    <div class="card" style="margin-top:8px;">
      <p><b>${escapeHtml(t("issue_label"))}</b> ${escapeHtml(f.issue)}</p>
      ${f.before ? `<p><i>${escapeHtml(t("before_label"))}</i> ${escapeHtml(f.before)}</p>` : ""}
      <p><i>${escapeHtml(t("after_label"))}</i> ${escapeHtml(f.after)}</p>
    </div>
  `).join("");

  actionArea().innerHTML = `
    ${cards}
    <div class="prompt-block">${escapeHtml(t("ready_to_apply"))}</div>
    <div class="row">
      <button onclick="applyDirectly()">${escapeHtml(t("apply_now"))}</button>
      ${state.improveCount < MAX_IMPROVES ? `<button class="secondary" onclick="showImproveUpload()">${escapeHtml(t("improve_cv_btn"))}</button>` : ''}
    </div>
  `;
  scrollToBottom();
}

function showImproveUpload() {
  actionArea().innerHTML = `
    <div class="hint">${escapeHtml(t("upload_updated_cv"))}</div>
    <input type="file" id="improve_cv_file" accept=".pdf,.docx" />
    <button onclick="uploadImprovedCV()">${escapeHtml(t("upload_improved_btn"))}</button>
    <div id="improve_result"></div>
  `;
  scrollToBottom();
}

async function uploadImprovedCV() {
  const fileInput = document.getElementById("improve_cv_file");
  const resultEl = document.getElementById("improve_result");
  const file = fileInput.files[0];
  if (!file) {
    resultEl.innerHTML = `<div class="error">${escapeHtml(t("choose_file_first"))}</div>`;
    return;
  }

  resultEl.innerHTML = `<div class="hint">${escapeHtml(t("reading_updated_cv"))}</div>`;
  const formData = new FormData();
  formData.append("init_data", tg.initData);
  formData.append("file", file);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);
  try {
    const res = await fetch("/api/upload-cv", { method: "POST", body: formData, signal: controller.signal });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      console.error("Improved CV upload failed:", res.status, body);
      const err = new Error(body.detail || "");
      if (res.status === 401) err.sessionExpired = true;
      throw err;
    }
    state.improveCount += 1;
    renderPostImproveChoice();
  } catch (err) {
    console.error("Improved CV upload failed:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("upload_failed")))}</div>`;
  } finally {
    clearTimeout(timeout);
  }
}

function renderPostImproveChoice() {
  if (state.improveCount >= MAX_IMPROVES) {
    actionArea().innerHTML = `
      <div class="hint">${escapeHtml(t("improve_limit_reached"))}</div>
      <button onclick="applyDirectly()">${escapeHtml(t("apply_now"))}</button>
    `;
    scrollToBottom();
    return;
  }
  actionArea().innerHTML = `
    <div class="prompt-block">${escapeHtml(t("improve_choice"))}</div>
    <div class="row">
      <button onclick="applyDirectly()">${escapeHtml(t("apply_now"))}</button>
      <button class="secondary" onclick="checkFit()">${escapeHtml(t("check_match_again"))}</button>
    </div>
  `;
  scrollToBottom();
}

function renderSaved() {
  actionArea().innerHTML = `
    <div class="hint">${escapeHtml(t("saved_confirmation"))}</div>
    <button class="secondary" onclick="showApplications()">${escapeHtml(t("view_my_applications"))}</button>
  `;
  scrollToBottom();
}

// ── CV vs JD analysis + roadmap ──────────────────────────────────────
function looksLikeUrl(text) {
  return /^https?:\/\/\S+$/.test(text.trim());
}

async function analyzeCV() {
  const jd = document.getElementById("jd_text").value.trim();
  const btn = document.getElementById("analyze_btn");
  const resultEl = document.getElementById("analysis-result");

  if (!looksLikeUrl(jd) && jd.length < 100) {
    resultEl.innerHTML = `<div class="error">${escapeHtml(t("jd_too_short_web"))}</div>`;
    return;
  }

  btn.disabled = true;
  resultEl.innerHTML = `<div class="hint">${escapeHtml(t(looksLikeUrl(jd) ? "analyzing_link_message_web" : "analyzing_message_web"))}</div>`;

  try {
    const data = await callApi("/api/cv-jd-analysis", { jd });
    if (data.limit_reached) {
      document.getElementById("jd-input-box").hidden = true;
      resultEl.innerHTML = `<div class="prompt-block">${escapeHtml(t("analysis_limit_reached"))}</div>`;
      const buyBox = document.createElement("div");
      resultEl.appendChild(buyBox);
      await renderBuyChecks(buyBox);
      return;
    }
    state.jd = data.jd_text;
    state.analysisLevel = data.level.assessment;
    state.analysisRemaining = data.remaining;
    state.analysisQuota = data.quota;
    updateChecksHeader(data.remaining, data.quota);
    document.getElementById("jd-input-box").hidden = true;
    renderAnalysisResult(data);
  } catch (err) {
    console.error("Analysis failed:", err);
    resultEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("analysis_failed_web")))}</div>`;
  } finally {
    btn.disabled = false;
  }
}

function renderAnalysisResult(data) {
  const el = document.getElementById("analysis-result");
  const ats = data.ats, xyz = data.xyz, tools = data.tools, level = data.level;

  const toolEmoji = { strong: "✅", mentioned: "🟡", not_found: "❌" };
  const toolLabelKey = { strong: "tool_strong", mentioned: "tool_mentioned", not_found: "tool_not_found" };

  const rewritesHtml = (xyz.rewrites || []).slice(0, 2).map(r => `
    <div class="card" style="margin-top:8px;">
      <p><i>${escapeHtml(t("before_label"))}</i> ${escapeHtml(r.original)}</p>
      <p><i>${escapeHtml(t("after_label"))}</i> ${escapeHtml(r.improved)}</p>
    </div>
  `).join("");

  const toolsHtml = Object.entries(tools || {}).map(([name, rating]) => `
    <div class="tool-row">
      <span>${toolEmoji[rating] || "•"} ${escapeHtml(name)}</span>
      <span>${escapeHtml(t(toolLabelKey[rating] || "tool_not_found"))}</span>
    </div>
  `).join("");

  el.innerHTML = `
    <div class="card">
      <h3>${escapeHtml(t("ats_heading"))} — ${ats.score}/100</h3>
      <div class="score-bar"><div class="score-bar-fill" style="width:${ats.score}%;"></div></div>
      <div>✅ <b>${escapeHtml(t("matched_label"))}</b> ${escapeHtml((ats.matched || []).join(", ") || "—")}</div>
      <div>❌ <b>${escapeHtml(t("missing_label"))}</b> ${escapeHtml((ats.missing || []).join(", ") || "—")}</div>
      <p>${escapeHtml(ats.verdict || "")}</p>
    </div>
    <div class="card" style="margin-top:12px;">
      <h3>${escapeHtml(t("xyz_heading"))}</h3>
      <div>${escapeHtml(t("xyz_passing_label"))} ${(xyz.passing || []).length}</div>
      <div>${escapeHtml(t("xyz_failing_label"))} ${(xyz.failing || []).length}</div>
      ${rewritesHtml ? `<p style="margin-top:8px;"><b>${escapeHtml(t("xyz_rewrites_label"))}</b></p>${rewritesHtml}` : ""}
    </div>
    <div class="card" style="margin-top:12px;">
      <h3>${escapeHtml(t("tools_heading"))}</h3>
      ${toolsHtml}
    </div>
    <div class="card" style="margin-top:12px;">
      <h3>${escapeHtml(t("level_heading"))} — ${escapeHtml(level.assessment)}</h3>
      <p>${escapeHtml(level.reasoning || "")}</p>
    </div>
    <button onclick="startRoadmap()">${escapeHtml(t("get_roadmap_btn"))}</button>
    <div id="roadmap-area"></div>
  `;
  scrollToBottom();
}

function startRoadmap() {
  document.getElementById("roadmap-area").innerHTML = "";
  loadRoadmapItem(1);
}

// Each roadmap item gets appended as its own permanent block (like the
// vacancy carousel keeps prior state around) instead of replacing the
// previous item's content - so "Phone Screen Prep" stays visible above
// "Technical Interview Prep" rather than vanishing when you continue.
async function loadRoadmapItem(item) {
  const areaEl = document.getElementById("roadmap-area");
  const blockId = `roadmap-item-${item}`;
  areaEl.insertAdjacentHTML("beforeend", `<div id="${blockId}"><div class="hint">${escapeHtml(t("analyzing_message_web"))}</div></div>`);
  scrollToBottom();
  const blockEl = document.getElementById(blockId);
  try {
    const data = await callApi("/api/roadmap-item", { jd: state.jd, level: state.analysisLevel, item });
    if (data.fixes) {
      renderRoadmapFixes(blockEl, data, item);
    } else {
      renderRoadmapText(blockEl, data, item);
    }
  } catch (err) {
    console.error("Roadmap item failed:", err);
    blockEl.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("roadmap_failed_web")))}</div>`;
  }
}

function renderRoadmapFixes(blockEl, data, item) {
  const cards = (data.fixes || []).map(f => `
    <div class="card" style="margin-top:8px;">
      <p><b>${escapeHtml(t("issue_label"))}</b> ${escapeHtml(f.issue)}</p>
      ${f.before ? `<p><i>${escapeHtml(t("before_label"))}</i> ${escapeHtml(f.before)}</p>` : ""}
      <p><i>${escapeHtml(t("after_label"))}</i> ${escapeHtml(f.after)}</p>
    </div>
  `).join("");
  blockEl.innerHTML = `
    <h3 style="margin-top:16px;">${escapeHtml(data.title)}</h3>
    ${cards}
    <div id="roadmap-next-${item}"></div>
  `;
  renderRoadmapNext(document.getElementById(`roadmap-next-${item}`), data.is_last, item);
  scrollToBottom();
}

function formatRoadmapText(raw) {
  const escaped = escapeHtml(raw || "");
  return escaped.split("\n").map(line => {
    const headerMatch = line.match(/^#{2,3}\s+(.*)/);
    if (headerMatch) return `<b>${headerMatch[1]}</b>`;
    return line.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  }).join("\n");
}

function renderRoadmapText(blockEl, data, item) {
  blockEl.innerHTML = `
    <div class="card" style="margin-top:16px;">
      <h3>${escapeHtml(data.title)}</h3>
      <div class="roadmap-body">${formatRoadmapText(data.text)}</div>
    </div>
    <div id="roadmap-next-${item}"></div>
  `;
  renderRoadmapNext(document.getElementById(`roadmap-next-${item}`), data.is_last, item);
  scrollToBottom();
}

function renderRoadmapNext(nextEl, isLast, item) {
  if (!isLast) {
    nextEl.innerHTML = `<button onclick="loadRoadmapItem(${item + 1})">${escapeHtml(t("roadmap_continue_btn"))}</button>`;
    return;
  }
  renderRoadmapDone(nextEl);
}

// The real next-step flow after finishing a roadmap: no dead end - tell
// the user exactly how many free checks they have left, and either offer
// to analyze another job or send them straight to buying more checks.
async function renderRoadmapDone(nextEl) {
  nextEl.innerHTML = `<div class="hint" style="margin-top:8px;">${escapeHtml(t("roadmap_done"))}</div><div id="post-roadmap-next"></div>`;
  const box = document.getElementById("post-roadmap-next");
  box.innerHTML = `<div class="hint">…</div>`;
  try {
    const q = await callApi("/api/quota-status", {});
    updateChecksHeader(q.remaining, q.quota);
    if (q.remaining <= 0) {
      box.innerHTML = `<div class="prompt-block">${escapeHtml(t("post_roadmap_no_checks"))}</div>`;
      const buyBox = document.createElement("div");
      box.appendChild(buyBox);
      await renderBuyChecks(buyBox);
    } else {
      box.innerHTML = `
        <div class="prompt-block">${escapeHtml(t("post_roadmap_checks_left", { remaining: q.remaining, quota: q.quota }))}</div>
        <button onclick="goToAnalysis()">${escapeHtml(t("analyze_another_btn"))}</button>
      `;
    }
  } catch (err) {
    console.error("Couldn't load quota status after roadmap:", err);
    box.innerHTML = `<button onclick="goToAnalysis()">${escapeHtml(t("analyze_another_btn"))}</button>`;
  }
  scrollToBottom();
}

// ── Buy checks (flexible pay-per-check pricing) ──────────────────────
function checksLabel(n) {
  return n === 1 ? `1 ${t("check_word_one")}` : `${n} ${t("checks_word")}`;
}

async function renderBuyChecks(containerEl) {
  containerEl.innerHTML = `<div id="buy-checks-box"><div class="hint">…</div></div>`;
  const box = document.getElementById("buy-checks-box");
  let price = 1000000;
  try {
    const q = await callApi("/api/quota-status", {});
    price = q.price_per_check_tiyin;
  } catch (err) {
    console.error("Couldn't load price, using fallback:", err);
  }
  const amountFor = n => Math.round(n * price / 100).toLocaleString();
  box.innerHTML = `
    <div class="prompt-block">${escapeHtml(t("buy_checks_intro", { price: (price / 100).toLocaleString() }))}</div>
    ${CHECK_QUANTITY_PRESETS.map(n => `<button onclick="buyChecks(${n})">${escapeHtml(checksLabel(n))} — ${amountFor(n)} UZS</button>`).join("")}
    <button class="secondary" onclick="showCustomChecksInput()">${escapeHtml(t("buy_custom_btn"))}</button>
    <div id="buy-checks-extra"></div>
  `;
  scrollToBottom();
}

function showCustomChecksInput() {
  document.getElementById("buy-checks-extra").innerHTML = `
    <div class="hint">${escapeHtml(t("buy_custom_prompt"))}</div>
    <input type="number" id="custom_checks_input" min="${MIN_CHECKS_PURCHASE}" max="${MAX_CHECKS_PURCHASE}" />
    <button onclick="submitCustomChecks()">${escapeHtml(t("buy_custom_confirm"))}</button>
    <div id="custom-checks-error"></div>
  `;
  scrollToBottom();
}

function submitCustomChecks() {
  const val = parseInt(document.getElementById("custom_checks_input").value, 10);
  const errEl = document.getElementById("custom-checks-error");
  if (!Number.isInteger(val) || val < MIN_CHECKS_PURCHASE || val > MAX_CHECKS_PURCHASE) {
    errEl.innerHTML = `<div class="error">${escapeHtml(t("buy_custom_invalid"))}</div>`;
    return;
  }
  buyChecks(val);
}

async function buyChecks(checks) {
  const box = document.getElementById("buy-checks-box");
  box.innerHTML = `<div class="hint">${escapeHtml(t("checkout_opening"))}</div>`;
  try {
    const data = await callApi("/api/checkout", { checks });
    if (tg && tg.openLink) {
      tg.openLink(data.checkout_url);
    } else {
      window.open(data.checkout_url, "_blank");
    }
  } catch (err) {
    console.error("Checkout failed:", err);
    box.innerHTML = `<div class="error">⚠️ ${escapeHtml(friendlyError(err, t("checkout_failed")))}</div>`;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}
