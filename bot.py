import logging
import os
import base64
import json
import asyncio
from datetime import datetime

import io
from pypdf import PdfReader

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)
from telegram.constants import ParseMode

load_dotenv()

import state
import coach
import formatter

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

WELCOME = (
    "👋 <b>AE Career Coach</b>\n\n"
    "Here is how I work:\n\n"
    "1️⃣ You upload your CV\n"
    "2️⃣ I suggest job titles that fit your profile\n"
    "3️⃣ You tell me location, work setup, and industry\n"
    "4️⃣ I search live job postings and score your CV against each one\n"
    "5️⃣ You pick a role to apply for\n"
    "6️⃣ I analyse your CV against that role step by step\n\n"
    "📄 <b>Upload your CV as a PDF to begin.</b>"
)

MAX_SEARCHES = 3


# ── Helpers ───────────────────────────────────────────────────────────────────

def log_event(user_id: int, event: str) -> None:
    entry = {"ts": datetime.utcnow().isoformat(), "user_id": user_id, "event": event}
    with open("usage.log", "a") as f:
        f.write(json.dumps(entry) + "\n")


def action_button(label: str, callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=callback)]])


# ── Commands ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    log_event(user_id, "started")
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.HTML)


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state.reset(update.effective_user.id)
    await update.message.reply_text(
        "🔄 Reset. Upload your CV to start again.",
        parse_mode=ParseMode.HTML,
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        return
    try:
        lines = open("usage.log").readlines()
    except FileNotFoundError:
        await update.message.reply_text("No data yet.")
        return

    events = []
    for line in lines:
        try:
            events.append(json.loads(line.strip()))
        except Exception:
            continue

    def total(event_name):
        return sum(1 for e in events if e.get("event") == event_name)

    def unique(event_name):
        return len(set(e["user_id"] for e in events if e.get("event") == event_name))

    await update.message.reply_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"<b>Started</b>\n"
        f"  Total: {total('started')} · Unique: {unique('started')}\n\n"
        f"<b>CV uploaded</b>\n"
        f"  Total: {total('cv_uploaded')} · Unique: {unique('cv_uploaded')}\n\n"
        f"<b>Role chosen</b>\n"
        f"  Total: {total('role_chosen')} · Unique: {unique('role_chosen')}\n\n"
        f"<b>Roadmap requested</b>\n"
        f"  Total: {total('roadmap_requested')} · Unique: {unique('roadmap_requested')}",
        parse_mode=ParseMode.HTML,
    )

# ── CV upload ─────────────────────────────────────────────────────────────────

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    doc = update.message.document

    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Please upload a <b>PDF</b> file.", parse_mode=ParseMode.HTML)
        return

    log_event(user_id, "cv_uploaded")
    msg = await update.message.reply_text("📄 Got your CV. Analysing your profile…")

    try:
        file = await context.bot.get_file(doc.file_id)
        cv_bytes = await file.download_as_bytearray()

        # Extract text once to save tokens on later calls
        reader = PdfReader(io.BytesIO(bytes(cv_bytes)))
        user["cv_text"] = "\n".join(page.extract_text() or "" for page in reader.pages)
        user["cv_b64"] = base64.b64encode(cv_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Download error: {e}")
        await msg.edit_text("❌ Could not read your CV. Please try again.")
        return

    try:
        titles = await coach.suggest_job_titles(user["cv_text"])
        user["suggested_titles"] = titles
        user["phase"] = "titles_suggested"
    except Exception as e:
        logger.error(f"Title suggestion error: {e}")
        await msg.edit_text("❌ Could not analyse your CV. Please try again.")
        return

    await msg.delete()

    buttons = [
        [InlineKeyboardButton(t, callback_data=f"title_{i}")]
        for i, t in enumerate(titles)
    ]
    buttons.append([InlineKeyboardButton("✏️ Enter my own title", callback_data="title_custom")])

    await update.message.reply_text(
        "Based on your CV, here are the roles that fit your profile.\n\n"
        "Which one are you targeting?",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── Text handler (custom inputs) ──────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    text = update.message.text.strip()
    message = update.message

    if user["phase"] == "waiting_title":
        user["job_title"] = text
        user["phase"] = "title_chosen"
        await message.reply_text(f"✅ <b>{text}</b> saved.", parse_mode=ParseMode.HTML)
        await ask_location(message, user_id)

    elif user["phase"] == "waiting_location":
        user["location"] = text
        user["phase"] = "location_chosen"
        await message.reply_text(f"📍 <b>{text}</b> saved.", parse_mode=ParseMode.HTML)
        await ask_setup(message)

    elif user["phase"] == "waiting_industry":
        user["industry"] = text
        user["phase"] = "industry_chosen"
        await message.reply_text(f"✅ <b>{text}</b> saved.", parse_mode=ParseMode.HTML)
        await start_search(message, context, user_id)

    else:
        await message.reply_text(
            "Send /start to begin or /reset to start over.",
            parse_mode=ParseMode.HTML,
        )


# ── Preference prompts ────────────────────────────────────────────────────────

async def ask_location(message, user_id: int) -> None:
    title = state.get(user_id)["job_title"]
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇪🇺 Europe", callback_data="loc_eu"),
            InlineKeyboardButton("🇺🇸 United States", callback_data="loc_us"),
        ],
        [InlineKeyboardButton("✏️ Enter location", callback_data="loc_custom")],
    ])
    await message.reply_text(
        f"Great — <b>{title}</b> it is.\n\nWhere are you looking?",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def ask_setup(message) -> None:
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🏠 Remote", callback_data="setup_remote"),
        InlineKeyboardButton("🏢 Office", callback_data="setup_office"),
        InlineKeyboardButton("🔀 Hybrid", callback_data="setup_hybrid"),
    ]])
    await message.reply_text(
        "Work setup preference?",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def ask_industry(message) -> None:
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏥 Health", callback_data="ind_health"),
            InlineKeyboardButton("💳 FinTech", callback_data="ind_fintech"),
        ],
        [InlineKeyboardButton("✏️ Enter industry", callback_data="ind_custom")],
    ])
    await message.reply_text(
        "Which industry?",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# ── Vacancy search & display ──────────────────────────────────────────────────

async def start_search(message, context, user_id: int) -> None:
    user = state.get(user_id)
    user["search_count"] += 1

    msg = await message.reply_text(
        f"🔍 Searching for a matching role… (search {user['search_count']} of {MAX_SEARCHES})",
        parse_mode=ParseMode.HTML,
    )

    try:
        vacancy = await coach.search_one_vacancy(
            user["job_title"], user["location"], user["work_setup"],
            user["industry"], user["seen_companies"]
        )
        if not vacancy:
            await msg.edit_text("No matching role found. Send /reset to try different filters.")
            return

        score = await coach.score_vacancy(user["cv_text"], vacancy)
        vacancy["score_data"] = score
        user["current_vacancy"] = vacancy
        user["seen_companies"].append(vacancy["company"])
        user["phase"] = "vacancy_browsing"
    except Exception as e:
        logger.error(f"Search error: {e}")
        await msg.edit_text("❌ Search failed. Send /reset and try again.")
        return

    await msg.delete()
    await show_vacancy(message, user_id)


async def show_vacancy(message, user_id: int) -> None:
    user = state.get(user_id)
    vacancy = user["current_vacancy"]
    text = formatter.vacancy_card(vacancy, vacancy["score_data"], user["search_count"], MAX_SEARCHES)

    row = []
    if user["search_count"] < MAX_SEARCHES:
        row.append(InlineKeyboardButton("Show me another →", callback_data="vac_another"))
    row.append(InlineKeyboardButton("Compare my CV to this role →", callback_data="vac_choose"))

    await message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([row]))


# ── CV analysis steps ─────────────────────────────────────────────────────────

async def run_analysis(message, user_id: int) -> None:
    user = state.get(user_id)
    vacancy = user["chosen_vacancy"]
    jd_text = (
        f"Role: {vacancy['title']}\n"
        f"Company: {vacancy['company']}\n"
        f"Location: {vacancy['location']}\n\n"
        f"{vacancy['summary']}"
    )

    msg = await message.reply_text("🔍 Analysing your CV against this role…")

    try:
        outputs = await coach.analyze_cv(jd_text, user["cv_text"])
        user["outputs"] = outputs
        user["level"] = outputs["level"]["assessment"]
        user["phase"] = "step_1"
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await msg.edit_text("❌ Analysis failed. Send /reset and try again.")
        return

    await msg.delete()
    text = formatter.step_ats(user["outputs"]["ats"])
    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=action_button("Check my CV writing →", "step_2"),
    )


# ── Callback handler ──────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user = state.get(user_id)
    action = query.data
    message = query.message

    await query.edit_message_reply_markup(reply_markup=None)

    # ── Job title
    if action.startswith("title_") and action != "title_custom":
        idx = int(action.split("_")[1])
        user["job_title"] = user["suggested_titles"][idx]
        user["phase"] = "title_chosen"
        await ask_location(message, user_id)

    elif action == "title_custom":
        user["phase"] = "waiting_title"
        await message.reply_text("Type the job title you are targeting 👇")

    # ── Location
    elif action == "loc_eu":
        user["location"] = "Europe"
        await ask_setup(message)

    elif action == "loc_us":
        user["location"] = "United States"
        await ask_setup(message)

    elif action == "loc_custom":
        user["phase"] = "waiting_location"
        await message.reply_text("Type your preferred location (city or country) 👇")

    # ── Work setup
    elif action in ("setup_remote", "setup_office", "setup_hybrid"):
        user["work_setup"] = action.split("_")[1].capitalize()
        await ask_industry(message)

    # ── Industry
    elif action == "ind_health":
        user["industry"] = "Healthcare"
        await start_search(message, context, user_id)

    elif action == "ind_fintech":
        user["industry"] = "FinTech"
        await start_search(message, context, user_id)

    elif action == "ind_custom":
        user["phase"] = "waiting_industry"
        await message.reply_text("Type the industry you are targeting 👇")

    # ── Vacancy browsing

    elif action == "vac_another":
        await start_search(message, context, user_id)

    elif action == "vac_choose":
        vacancy = user["current_vacancy"]
        user["chosen_vacancy"] = vacancy
        log_event(user_id, "role_chosen")
        await message.reply_text(
            f"✅ <b>{vacancy['title']}</b> @ <b>{vacancy['company']}</b> selected.\n\n"
            f"Now let me analyse your CV against this role.",
            parse_mode=ParseMode.HTML,
        )
        await run_analysis(message, user_id)

    # ── Analysis steps
    elif action == "step_2":
        user["phase"] = "step_2"
        await message.reply_text(
            formatter.step_xyz(user["outputs"]["xyz"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("See my skill gaps →", "step_3"),
        )

    elif action == "step_3":
        user["phase"] = "step_3"
        await message.reply_text(
            formatter.step_tools(user["outputs"]["tools"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("Assess my level →", "step_4"),
        )

    elif action == "step_4":
        user["phase"] = "step_4"
        await message.reply_text(
            formatter.step_level(user["outputs"]["level"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("Get my roadmap →", "step_5"),
        )

    elif action == "step_5":
        user["phase"] = "step_5"
        log_event(user_id, "roadmap_requested")
        vacancy = user["chosen_vacancy"]
        jd_text = f"Role: {vacancy['title']}\nCompany: {vacancy['company']}\n\n{vacancy['summary']}"

        loading = await message.reply_text(
            formatter.step_roadmap_header(user["level"]),
            parse_mode=ParseMode.HTML,
        )
        try:
            roadmap = await coach.generate_roadmap(user["level"], jd_text, user["cv_text"])
        except Exception as e:
            logger.error(f"Roadmap error: {e}")
            await loading.edit_text("❌ Roadmap generation failed. Send /reset to try again.")
            return

        await loading.delete()
        formatted = formatter.format_roadmap(roadmap)
        header = f"<b>🗺 Your Roadmap — {user['level']}</b>\n\n"
        for chunk in formatter.split_long(header + formatted):
            await message.reply_text(chunk, parse_mode=ParseMode.HTML)

        user["phase"] = "done"
        await message.reply_text(
            "✅ Done. Send /reset to analyse another role.",
            parse_mode=ParseMode.HTML,
        )


# ── Error handler ─────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception", exc_info=context.error)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN not set")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)

    logger.info("Bot starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
