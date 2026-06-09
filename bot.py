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

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

WELCOME = (
    "👋 <b>AE Career Coach</b>\n\n"
    "1️⃣ Upload your CV as a PDF\n"
    "2️⃣ Paste the job description you are targeting\n"
    "3️⃣ I analyse your CV against it step by step\n\n"
    "📄 <b>Upload your CV to begin.</b>"
)


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
    await update.message.reply_text("🔄 Reset. Upload your CV to start again.")


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
        f"Roadmap — Total {total('roadmap_requested')} · Unique {unique('roadmap_requested')}",
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

    if len(text) < 100:
        await update.message.reply_text("That looks too short. Please paste the full job description.")
        return

    user["jd"] = text
    user["phase"] = "analyzing"

    msg = await update.message.reply_text("🔍 Analysing your CV against this role…")
    try:
        outputs = await coach.analyze_cv(user["jd"], user["cv_text"])
        user["outputs"] = outputs
        user["level"] = outputs["level"]["assessment"]
        user["phase"] = "step_1"
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await msg.edit_text("❌ Analysis failed. Send /reset and try again.")
        return

    await msg.delete()
    await update.message.reply_text(
        formatter.step_ats(outputs["ats"]),
        parse_mode=ParseMode.HTML,
        reply_markup=action_button("Check my CV writing →", "step_2"),
    )


# ── Step callbacks ────────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user = state.get(user_id)
    action = query.data
    message = query.message

    await query.edit_message_reply_markup(reply_markup=None)

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
        loading = await message.reply_text(
            formatter.step_roadmap_header(user["level"]),
            parse_mode=ParseMode.HTML,
        )
        try:
            roadmap = await coach.generate_roadmap(user["level"], user["jd"], user["cv_text"])
        except Exception as e:
            logger.error(f"Roadmap error: {e}")
            await loading.edit_text("❌ Roadmap failed. Send /reset to try again.")
            return

        await loading.delete()
        formatted = formatter.format_roadmap(roadmap)
        header = f"<b>🗺 Your Roadmap — {user['level']}</b>\n\n"
        for chunk in formatter.split_long(header + formatted):
            await message.reply_text(chunk, parse_mode=ParseMode.HTML)

        await message.reply_text("✅ Done. Send /reset to analyse another role.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception", exc_info=context.error)


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