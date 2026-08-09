# AE Career Coach — Telegram Bot

Analyses a candidate's CV against a job description and delivers a personalised Analytics Engineering career roadmap.

## Flow

```
/start
  → User pastes job description
  → User uploads CV (PDF)
  → Step 1: ATS Score        [Continue →]
  → Step 2: XYZ Formula Check [Continue →]
  → Step 3: Tool Radar        [Continue →]
  → Step 4: Level Assessment  [Continue →]
  → Step 5: Full Roadmap (with live job search)
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

pip install -r requirements.txt
python bot.py
```

## Deploy on Railway (free tier)

1. Push to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select your repo
4. In the same project: New → Database → Add PostgreSQL
5. In the bot service's Variables tab, add a reference to the Postgres `DATABASE_URL` (Railway's "Add Reference" option), plus `TELEGRAM_TOKEN` and `ANTHROPIC_API_KEY`
6. Railway auto-detects Python and runs `python bot.py`

No Dockerfile needed. Free tier is enough for low-traffic usage.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Main entry point, all Telegram handlers |
| `coach.py` | Anthropic API calls (analyze + roadmap) |
| `state.py` | Per-user conversation state (Postgres-backed, in-memory cache) |
| `prompts.py` | All Claude prompts per level |
| `formatter.py` | Format outputs as Telegram HTML |

## Notes

- State is cached in memory but persisted to Postgres as JSONB (one row per user) — survives restarts/redeploys. Requires `DATABASE_URL`.
- Step 5 uses Anthropic's built-in web search tool to find live job openings.
- `/reset` clears a user's state and restarts the flow.
