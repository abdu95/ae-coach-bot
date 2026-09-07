# AcceptedAI — Telegram Bot (launcher)

This bot is a thin launcher: language picker, one-time name capture, admin/pilot commands, and a single
"Open AcceptedAI" button that opens the Mini App. Every actual feature — CV-vs-JD analysis + roadmap,
vacancy search + application tracking, and payment — lives in the Mini App, in the sister repo
[`vacancy-webapp`](https://github.com/abdu95/vacancy-webapp) (its own Railway service).

## Flow

```
/start (or /app, /reset, or any stray message)
  → language picker (first time) + one-time name capture
  → short explainer + "Open AcceptedAI" button → opens the Mini App
```

## Local Setup

### 1. Get a Telegram bot token

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow the prompts
3. Copy the token

### 2. Get your Anthropic API key

https://console.anthropic.com → API Keys → Create Key

### 3. Get a Postgres database

State is persisted to Postgres (see Notes below). For local dev, run one via Docker:

```bash
docker run -d --name ae-coach-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
```

Then set `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres` in `.env`.

### 4. Install and run

```bash
git clone <your-repo>
cd ae-coach-bot

cp .env.example .env
# Edit .env and add your tokens and DATABASE_URL

cd bot
pip install -r requirements.txt
python bot.py
```

## Deploy on Railway (free tier)

1. Push to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select this repo
4. In the bot service's Settings → Source, set **Root Directory** to `bot`
5. In the same project: New → Database → Add PostgreSQL
6. In the bot service's Variables tab, add a reference to the Postgres `DATABASE_URL` (Railway's "Add Reference" option), plus `TELEGRAM_TOKEN`, `MINI_APP_URL` (the Mini App's public URL), and `ADMIN_IDS`
7. Railway auto-detects Python and runs `python bot.py`

The Mini App (`vacancy-webapp`) is a separate Railway project/service deployed from its own repo —
see that repo's README for its setup. Both share the same Postgres instance (add a `DATABASE_URL`
reference on that service too).

No Dockerfile needed. Free tier is enough for low-traffic usage.

## Files

| File | Purpose |
|---|---|
| `bot/bot.py` | Main entry point — launcher flow, admin/pilot/marketing commands |
| `bot/state.py` | Per-user account state (Postgres-backed, in-memory cache), quota, orders, stats |
| `bot/i18n.py` | uz/ru/en strings |

## Notes

- State is cached in memory but persisted to Postgres as JSONB/relational tables (one row per user/event) — survives restarts/redeploys. Requires `DATABASE_URL`.
- `/reset` clears a user's cached name/session and re-sends the launcher.
