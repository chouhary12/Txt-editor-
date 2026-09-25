# Telegram TXT Tools Bot

A Pyrogram Telegram bot for working with TXT files.

## Features

- 🔎 Compare OLD TXT vs NEW TXT and return only **new URLs**
- 🔗 Extract unique URLs from a TXT
- 🧹 Clean TXT (remove blank lines and duplicate lines)
- 📊 TXT statistics
- 🔀 Merge two TXT files
- ♻️ Find duplicate lines
- 🔒 Force subscription to `@inventor_king_24`
- 📦 Configurable TXT file size limit (default 20 MB)
- Supports common encodings: UTF-8, UTF-8 BOM, UTF-16 and Latin-1
- Heroku worker ready
- No secrets hard-coded in source

## Important

For force-subscription, the bot must be able to check membership in the target channel. Add the bot to the channel with sufficient permissions for membership checks.

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set:

```text
API_ID=...
API_HASH=...
BOT_TOKEN=...
FORCE_SUB_CHANNEL=@inventor_king_24
FORCE_SUB_URL=https://t.me/inventor_king_24
MAX_FILE_MB=20
```

Then export those variables (or use your preferred dotenv loader) and run:

```bash
python main.py
```

## Heroku deployment

This repo is configured as a **worker** because a Telegram polling bot is a long-running background process.

### Option A — Git deployment

```bash
heroku login
heroku create your-txt-tools-bot

heroku config:set API_ID=YOUR_API_ID
heroku config:set API_HASH=YOUR_API_HASH
heroku config:set BOT_TOKEN=YOUR_BOT_TOKEN
heroku config:set FORCE_SUB_CHANNEL=@inventor_king_24
heroku config:set FORCE_SUB_URL=https://t.me/inventor_king_24
heroku config:set MAX_FILE_MB=20

git init
git add .
git commit -m "Initial TXT Tools Bot"
git branch -M main
git push heroku main

heroku ps:scale worker=1
heroku logs --tail
```

### Option B — Heroku Dashboard

Create an app, connect/push this repository, then add these Config Vars:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `FORCE_SUB_CHANNEL`
- `FORCE_SUB_URL`
- `MAX_FILE_MB`

The included `Procfile` starts:

```text
worker: python main.py
```

## GitHub

Do not commit `.env`, bot tokens, API hashes or Telegram session files.

```bash
git init
git add .
git commit -m "Initial TXT Tools Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Usage

### New Links

1. `/compare`
2. Upload OLD `.txt`
3. Upload NEW `.txt`
4. Bot returns `new_links.txt`

Only URLs that occur in NEW but not in OLD are returned.

### Other commands

- `/extract`
- `/clean`
- `/stats`
- `/merge`
- `/duplicates`
- `/help`

## Notes

- Temporary downloaded files are deleted after processing.
- User workflow state is kept in memory, so keep a single worker (`worker=1`) unless you later add persistent storage.
- For large-scale usage, add Redis/Postgres and persistent job state.
