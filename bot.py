import logging
import os
import base64

import json
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

import state
import coach
import formatter

load_dotenv()
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def log_event(user_id: int, event: str):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "event": event
    }
    with open("usage.log", "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── Keyboard helpers ──────────────────────────────────────────────────────────

def continue_button(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Continue →", callback_data=callback)]])


# ── Command handlers ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    log_event(user_id, "started")
    await update.message.reply_text(
        "👋 <b>Analytics Engineer Career Coach</b>\n\n"
        "I will analyse your CV against a real job description and give you a personalised roadmap.\n\n"
        "First, <b>paste the job description</b> you are targeting — copy the full text from the job posting.",
        parse_mode=ParseMode.HTML,
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    await update.message.reply_text(
        "🔄 Reset. Send me a job description to start over.",
        parse_mode=ParseMode.HTML,
    )


MY_USER_ID = int(os.getenv("ADMIN_USER_ID"))  # ← paste your ID here

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != MY_USER_ID:
        return  # silently ignore, don't even reply
    
    try:
        with open("usage.log", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        await update.message.reply_text("No usage data yet.")
        return

    started = sum(1 for l in lines if "started" in l)
    cv_uploaded = sum(1 for l in lines if "cv_uploaded" in l)
    roadmap = sum(1 for l in lines if "roadmap_requested" in l)

    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"Started: {started}\n"
        f"CV uploaded: {cv_uploaded}\n"
        f"Roadmap requested: {roadmap}",
        parse_mode="Markdown"
    )

# ── Message handler (text = JD input) ────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    text = update.message.text.strip()

    if user["phase"] != "idle":
        await update.message.reply_text(
            "Send /reset to start over, or upload your CV if you have already pasted a JD.",
            parse_mode=ParseMode.HTML,
        )
        return

    if len(text) < 100:
        await update.message.reply_text(
            "That looks too short for a job description. Please paste the full JD text.",
            parse_mode=ParseMode.HTML,
        )
        return

    user["jd"] = text
    user["phase"] = "jd_received"
    log_event(user_id, "jd_submitted")

    await update.message.reply_text(
        "✅ <b>Job description saved.</b>\n\n"
        "Now <b>upload your CV as a PDF file</b>.",
        parse_mode=ParseMode.HTML,
    )


# ── Document handler (CV upload) ──────────────────────────────────────────────

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    doc = update.message.document

    if user["phase"] == "idle":
        await update.message.reply_text(
            "Please paste a job description first. Send /start to begin.",
            parse_mode=ParseMode.HTML,
        )
        return

    if user["phase"] != "jd_received":
        await update.message.reply_text(
            "Send /reset to start over.",
            parse_mode=ParseMode.HTML,
        )
        return

    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text(
            "Please upload a <b>PDF</b> file.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Download and encode CV
    user["phase"] = "analyzing"
    status_msg = await update.message.reply_text(
        "📄 CV received. Analysing… this takes about 20 seconds.",
        parse_mode=ParseMode.HTML,
    )
    log_event(user_id, "cv_uploaded") 

    try:
        file = await context.bot.get_file(doc.file_id)
        cv_bytes = await file.download_as_bytearray()
        user["cv_b64"] = base64.b64encode(cv_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"File download error: {e}")
        await status_msg.edit_text("❌ Could not download your CV. Please try again.")
        user["phase"] = "jd_received"
        return

    # Run analysis
    try:
        outputs = await coach.analyze_cv(user["jd"], user["cv_b64"])
        user["outputs"] = outputs
        user["level"] = outputs["level"]["assessment"]
    except Exception as e:
        logger.error(f"Claude analysis error: {e}")
        await status_msg.edit_text(
            "❌ Analysis failed. Please try again or send /reset."
        )
        user["phase"] = "jd_received"
        return

    await status_msg.delete()

    # Show Output 1
    user["phase"] = "output_1"
    msg = formatter.output_1(outputs["ats"])
    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.HTML,
        reply_markup=continue_button("output_2"),
    )


# ── Callback handler (Continue buttons) ──────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = state.get(user_id)
    action = query.data

    # Remove the Continue button from the previous message
    await query.edit_message_reply_markup(reply_markup=None)

    if action == "output_2":
        user["phase"] = "output_2"
        msg = formatter.output_2(user["outputs"]["xyz"])
        await query.message.reply_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=continue_button("output_3"),
        )

    elif action == "output_3":
        user["phase"] = "output_3"
        msg = formatter.output_3(user["outputs"]["tools"])
        await query.message.reply_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=continue_button("output_4"),
        )

    elif action == "output_4":
        user["phase"] = "output_4"
        msg = formatter.output_4(user["outputs"]["level"])
        await query.message.reply_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=continue_button("output_5"),
        )

    elif action == "output_5":
        user["phase"] = "output_5"
        log_event(user_id, "roadmap_requested")

        # Show loading message
        loading = await query.message.reply_text(
            formatter.output_5_header(user["level"]),
            parse_mode=ParseMode.HTML,
        )

        try:
            roadmap_text = await coach.generate_roadmap(
                user["level"], user["jd"], user["cv_b64"]
            )
        except Exception as e:
            logger.error(f"Roadmap generation error: {e}")
            await loading.edit_text("❌ Roadmap generation failed. Send /reset to try again.")
            return

        await loading.delete()

        # Format and send (split if over 4000 chars)
        formatted = formatter.format_roadmap(roadmap_text)
        header = f"<b>🗺 Output 5 — Your Roadmap ({user['level']})</b>\n\n"
        chunks = formatter.split_long(header + formatted)

        for chunk in chunks:
            await query.message.reply_text(chunk, parse_mode=ParseMode.HTML)

        # Done — offer reset
        user["phase"] = "done"
        await query.message.reply_text(
            "✅ <b>Done.</b> Send /reset to assess another CV.",
            parse_mode=ParseMode.HTML,
        )


# ── Error handler ─────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception", exc_info=context.error)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN not set in environment")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
