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

### 3. Install and run

```bash
git clone <your-repo>
cd ae-coach-bot

cp .env.example .env
# Edit .env and add your tokens

pip install -r requirements.txt
python bot.py
```

## Deploy on Railway (free tier)

1. Push to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select your repo
4. Add environment variables: `TELEGRAM_TOKEN` and `ANTHROPIC_API_KEY`
5. Railway auto-detects Python and runs `python bot.py`

No Dockerfile needed. Free tier is enough for low-traffic usage.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Main entry point, all Telegram handlers |
| `coach.py` | Anthropic API calls (analyze + roadmap) |
| `state.py` | Per-user conversation state (in-memory) |
| `prompts.py` | All Claude prompts per level |
| `formatter.py` | Format outputs as Telegram HTML |

## Notes

- State is in-memory — resets if the bot restarts. For persistence, replace the dict in `state.py` with SQLite.
- Step 5 uses Anthropic's built-in web search tool to find live job openings.
- `/reset` clears a user's state and restarts the flow.
