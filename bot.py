import logging
import os
import io
import json
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)
from telegram.constants import ParseMode
from pypdf import PdfReader

load_dotenv()

import state
import coach
import formatter
import i18n

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
USAGE_LIMIT = 3


def log_event(user_id: int, event: str) -> None:
    entry = {"ts": datetime.utcnow().isoformat(), "user_id": user_id, "event": event}
    with open("usage.log", "a") as f:
        f.write(json.dumps(entry) + "\n")


def action_button(label: str, callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=callback)]])


LANG_BUTTONS = {
    "uz": ("🇺🇿 O'zbek", "lang_uz"),
    "ru": ("🇷🇺 Русский", "lang_ru"),
}


async def send_language_picker(message, hint_code: str | None) -> None:
    # language_code reflects the device's system language, not necessarily
    # the user's preferred chat language — used only to order the buttons.
    order = ["ru", "uz"] if hint_code == "ru" else ["uz", "ru"]
    buttons = [[InlineKeyboardButton(LANG_BUTTONS[c][0], callback_data=LANG_BUTTONS[c][1])] for c in order]
    await message.reply_text(
        "🌐 Choose your language / Tilni tanlang / Выберите язык",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def send_limit_reached(message, lang: str) -> None:
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton(i18n.t("join_waitlist_button", lang), callback_data="join_waitlist")
    ]])
    await message.reply_text(
        i18n.limit_reached(USAGE_LIMIT, lang),
        parse_mode=ParseMode.HTML,
        reply_markup=buttons,
    )


# ── Commands ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    log_event(user_id, "started")
    user = state.get(user_id)
    if not user["lang"]:
        await send_language_picker(update.message, update.effective_user.language_code)
    else:
        await update.message.reply_text(i18n.t("welcome", user["lang"]), parse_mode=ParseMode.HTML)


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state.reset(update.effective_user.id)
    await update.message.reply_text("🔄 Reset. Upload your CV to start again.")


async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_language_picker(update.message, update.effective_user.language_code)


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
    total = lambda e: sum(1 for x in events if x.get("event") == e)
    unique = lambda e: len(set(x["user_id"] for x in events if x.get("event") == e))
    await update.message.reply_text(
        f"📊 <b>Stats</b>\n\n"
        f"Started — Total {total('started')} · Unique {unique('started')}\n"
        f"CV uploaded — Total {total('cv_uploaded')} · Unique {unique('cv_uploaded')}\n"
        f"Roadmap — Total {total('roadmap_requested')} · Unique {unique('roadmap_requested')}\n"
        f"Waitlist — {state.waitlist_count()}",
        parse_mode=ParseMode.HTML,
    )


# ── CV upload ─────────────────────────────────────────────────────────────────

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    doc = update.message.document

    if user["usage_count"] >= USAGE_LIMIT:
        await send_limit_reached(update.message, user["lang"])
        return

    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Please upload a <b>PDF</b> file.", parse_mode=ParseMode.HTML)
        return

    log_event(user_id, "cv_uploaded")
    msg = await update.message.reply_text("📄 Reading your CV…")

    try:
        file = await context.bot.get_file(doc.file_id)
        cv_bytes = await file.download_as_bytearray()
        reader = PdfReader(io.BytesIO(bytes(cv_bytes)))
        user["cv_text"] = "\n".join(page.extract_text() or "" for page in reader.pages)
        user["phase"] = "waiting_jd"
    except Exception as e:
        logger.error(f"CV read error: {e}")
        await msg.edit_text("❌ Could not read your CV. Please try again.")
        return

    await msg.delete()
    await update.message.reply_text(
        "✅ CV received.\n\nNow <b>paste the full job description</b> you are targeting.",
        parse_mode=ParseMode.HTML,
    )


# ── JD text → run analysis ────────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    text = update.message.text.strip()

    if user["phase"] != "waiting_jd":
        await update.message.reply_text("Send /start to begin or /reset to start over.")
        return

    if user["usage_count"] >= USAGE_LIMIT:
        await send_limit_reached(update.message, user["lang"])
        return

    if len(text) < 100:
        await update.message.reply_text("That looks too short. Please paste the full job description.")
        return

    user["jd"] = text
    user["phase"] = "analyzing"

    msg = await update.message.reply_text(
        i18n.t("analyzing", user["lang"]), parse_mode=ParseMode.HTML
    )
    try:
        outputs = await coach.analyze_cv(user["jd"], user["cv_text"])
        user["outputs"] = outputs
        user["level"] = outputs["level"]["assessment"]
        user["phase"] = "step_1"
        user["usage_count"] += 1
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await msg.edit_text("❌ Analysis failed. Send /reset and try again.")
        return

    await msg.delete()
    remaining = max(0, USAGE_LIMIT - user["usage_count"])
    await update.message.reply_text(
        formatter.step_ats(outputs["ats"]) + f"\n\n{i18n.checks_left(remaining, USAGE_LIMIT, user['lang'])}",
        parse_mode=ParseMode.HTML,
        reply_markup=action_button("Check my CV writing →", "step_2"),
    )


# ── Step callbacks ────────────────────────────────────────────────────────────

async def send_roadmap_item(message, user_id: int, item: int) -> None:
    user = state.get(user_id)
    level = user["level"]
    title = coach.roadmap_block_title(level, item)

    loading = await message.reply_text(
        i18n.roadmap_loading(item, title, user["lang"]),
        parse_mode=ParseMode.HTML,
    )
    try:
        text = await coach.generate_roadmap(level, item, user["jd"], user["cv_text"])
    except Exception as e:
        logger.error(f"Roadmap error (item {item}): {e}")
        await loading.edit_text("❌ Roadmap generation failed. Send /reset to try again.")
        return

    await loading.delete()
    formatted = formatter.step_roadmap_block(item, title, text)

    if item < 3:
        next_title = coach.roadmap_block_title(level, item + 1)
        chunks = formatter.split_long(formatted)
        for chunk in chunks[:-1]:
            await message.reply_text(chunk, parse_mode=ParseMode.HTML)
        await message.reply_text(
            chunks[-1],
            parse_mode=ParseMode.HTML,
            reply_markup=action_button(f"Continue: {next_title} →", f"step_5_{item + 1}"),
        )
    else:
        for chunk in formatter.split_long(formatted):
            await message.reply_text(chunk, parse_mode=ParseMode.HTML)
        await message.reply_text("✅ Done. Send /reset to analyse another role.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user = state.get(user_id)
    action = query.data
    message = query.message

    await query.edit_message_reply_markup(reply_markup=None)

    if action in ("lang_uz", "lang_ru"):
        user["lang"] = "uz" if action == "lang_uz" else "ru"
        await message.reply_text(i18n.t("welcome", user["lang"]), parse_mode=ParseMode.HTML)
        return

    if action == "join_waitlist":
        state.join_waitlist(user_id, update.effective_user.username)
        user["waitlisted"] = True
        await message.reply_text(i18n.t("waitlist_joined", user["lang"]))
        return

    if not user.get("outputs"):
        await message.reply_text("Session expired. Send /reset to start over.")
        return

    if action == "step_2":
        await message.reply_text(
            formatter.step_xyz(user["outputs"]["xyz"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("See my skill gaps →", "step_3"),
        )

    elif action == "step_3":
        await message.reply_text(
            formatter.step_tools(user["outputs"]["tools"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("Assess my level →", "step_4"),
        )

    elif action == "step_4":
        await message.reply_text(
            formatter.step_level(user["outputs"]["level"]),
            parse_mode=ParseMode.HTML,
            reply_markup=action_button("Get my roadmap →", "step_5"),
        )

    elif action == "step_5":
        log_event(user_id, "roadmap_requested")
        await send_roadmap_item(message, user_id, item=1)

    elif action in ("step_5_2", "step_5_3"):
        item = 2 if action == "step_5_2" else 3
        await send_roadmap_item(message, user_id, item=item)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception", exc_info=context.error)


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN not set")

    state.init_db()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", state.persisting(start)))
    app.add_handler(CommandHandler("reset", state.persisting(reset_cmd)))
    app.add_handler(CommandHandler("language", state.persisting(language_cmd)))
    app.add_handler(CommandHandler("stats", state.persisting(stats)))
    app.add_handler(MessageHandler(filters.Document.PDF, state.persisting(handle_document)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, state.persisting(handle_text)))
    app.add_handler(CallbackQueryHandler(state.persisting(handle_callback)))
    app.add_error_handler(error_handler)

    logger.info("Bot starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()