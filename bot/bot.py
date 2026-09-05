import logging
import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)
from telegram.constants import ParseMode

load_dotenv()

import state
import i18n

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", os.getenv("ADMIN_USER_ID", "0")).split(",") if x.strip()
}
PILOT_CODE = os.getenv("PILOT_CODE", "school21")
# /start deep-link tags for tracking marketing campaigns -> users.source.
# e.g. t.me/<bot>?start=chashma for the chashma.uz half-marathon link.
MARKETING_SOURCES = {"chashma": "chashma_marathon"}
PILOT_QUOTA = int(os.getenv("PILOT_QUOTA", "10"))
PILOT_CAP = int(os.getenv("PILOT_CAP", "10"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "")


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


def app_open_markup(lang: str) -> InlineKeyboardMarkup | None:
    if not MINI_APP_URL:
        return None
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(i18n.t("app_open_button", lang), web_app=WebAppInfo(url=MINI_APP_URL))
    ]])


async def send_launcher(message, user: dict) -> None:
    """The bot's entire product surface: a short explainer plus one button
    that opens the Mini App. Everything else (CV analysis, vacancy search,
    tracking, payment) lives inside the app - this is reused by /start,
    /app, /reset, and as the fallback for any stray text message."""
    markup = app_open_markup(user["lang"])
    if markup is None:
        await message.reply_text(i18n.t("app_not_configured", user["lang"]))
        return
    await message.reply_text(
        i18n.t("app_intro", user["lang"]),
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
    )


# ── Commands ──────────────────────────────────────────────────────────────────

async def enroll_pilot(message, user_id: int, lang: str) -> None:
    if state.get_source(user_id) == "school21_pilot":
        await message.reply_text(i18n.t("pilot_already", lang))
        return
    if state.pilot_count() >= PILOT_CAP:
        await message.reply_text(i18n.t("pilot_full", lang))
        return
    state.set_quota_override(user_id, PILOT_QUOTA, source="school21_pilot")
    state.log_event(user_id, "pilot_enrolled")
    await message.reply_text(i18n.pilot_enrolled(PILOT_QUOTA, lang))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    state.log_event(user_id, "started")
    user = state.get(user_id)

    if context.args and context.args[0] == PILOT_CODE:
        await enroll_pilot(update.message, user_id, user["lang"])
    elif context.args and context.args[0] in MARKETING_SOURCES:
        state.set_source(user_id, MARKETING_SOURCES[context.args[0]])
        state.log_event(user_id, "marketing_source_start", metadata={"source": context.args[0]})

    if not user["lang"]:
        await send_language_picker(update.message, update.effective_user.language_code)
    elif not user["name"]:
        user["phase"] = "waiting_name"
        await update.message.reply_text(i18n.t("ask_name", user["lang"]))
    else:
        await send_launcher(update.message, user)


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state.reset(user_id)
    state.log_event(user_id, "reset")
    user = state.get(user_id)
    await update.message.reply_text(i18n.t("reset_done", user["lang"]))
    await send_launcher(update.message, user)


async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_language_picker(update.message, update.effective_user.language_code)


async def app_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Calling state.get() here (even though this handler doesn't use the
    session data) ensures a `users` row exists for this telegram_id.
    Without it, a user who only ever taps /app (never /start) would have
    no `users` row, and saving an application later would fail - the
    applications table has telegram_id REFERENCES users(telegram_id)."""
    user = state.get(update.effective_user.id)
    await send_launcher(update.message, user)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    acct = state.account_stats()
    pilot = state.pilot_stats()
    ev = state.event_stats(
        ["started", "name_provided", "check_completed", "roadmap_requested", "reset"]
    )
    chashma_count = state.source_count("chashma_marathon")

    def line(label: str, key: str) -> str:
        total, unique = ev[key]
        return f"{label} — Total {total} · Unique {unique}"

    await update.message.reply_text(
        f"📊 <b>Stats</b>\n\n"
        f"Unique users — {acct['unique_users']}\n"
        f"Activated (≥1 check) — {acct['activated_users']}\n"
        f"Total checks run — {acct['total_checks']}\n\n"
        f"{line('Started', 'started')}\n"
        f"{line('Name provided', 'name_provided')}\n"
        f"{line('Check completed', 'check_completed')}\n"
        f"{line('Roadmap requested', 'roadmap_requested')}\n"
        f"{line('Reset', 'reset')}\n\n"
        f"Waitlist — {acct['waitlist']}\n\n"
        f"🎓 School21 pilot — {pilot['users']} users · {pilot['checks']} checks · avg {pilot['avg']}/user\n"
        f"🏃 Chashma marathon — {chashma_count} users\n\n"
        f"Note: 'Check completed'/'Roadmap requested' now happen inside the Mini App, "
        f"which doesn't log these bot-side events yet — treat as historical/chat-only "
        f"until the app logs its own.",
        parse_mode=ParseMode.HTML,
    )


async def grant_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Usage: /grant <telegram_id> [quota]")
        return
    try:
        target_id = int(context.args[0])
        quota = int(context.args[1]) if len(context.args) > 1 else PILOT_QUOTA
    except ValueError:
        await update.message.reply_text("Usage: /grant <telegram_id> [quota]")
        return
    if state.set_quota_override(target_id, quota):
        await update.message.reply_text(f"✅ Granted quota={quota} to {target_id}.")
    else:
        await update.message.reply_text(f"⚠️ {target_id} has never messaged the bot — nothing to grant.")


# ── Text / callback fallbacks ─────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = state.get(user_id)
    text = update.message.text.strip()

    if user["phase"] == "waiting_name":
        name = text[:50]
        user["name"] = name
        user["phase"] = "idle"
        state.log_event(user_id, "name_provided")
        await update.message.reply_text(i18n.stats_and_privacy(name, user["lang"]))
        await send_launcher(update.message, user)
        return

    # Any other text (the bot no longer runs a chat flow) - redirect to the app.
    await send_launcher(update.message, user)


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
        if user["name"]:
            await send_launcher(message, user)
        else:
            user["phase"] = "waiting_name"
            await message.reply_text(i18n.t("ask_name", user["lang"]))
        return


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
    app.add_handler(CommandHandler("app", state.persisting(app_cmd)))
    app.add_handler(CommandHandler("stats", state.persisting(stats)))
    app.add_handler(CommandHandler("grant", state.persisting(grant_cmd)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, state.persisting(handle_text)))
    app.add_handler(CallbackQueryHandler(state.persisting(handle_callback)))
    app.add_error_handler(error_handler)

    logger.info("Bot starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
