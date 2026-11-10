# Potoo Corporate Climb — Study & Career Accountability Bot

This package **upgrades your existing Discord setup**. It includes the previous `setup_discord.py` for creating the 7 categories and 23 channels, plus a separate long-running `career_bot.py`.

## What it does

- **Every day 08:00 UK time:** posts a morning prompt in `#daily-check-in`
- **Every day 20:00 UK time:** posts an evening reflection in `#daily-check-in`
- **Every Sunday 19:00 UK time:** posts tracked weekly totals and prompts in `#weekly-review`
- `/checkin goal:...` logs a daily goal and posts it to the check-in channel
- `/study minutes:... topic:... notes:...` logs study minutes and posts a study note
- `/application company:... role:... stage:... next_step:...` records a job event in `#applications-tracker`
- `/progress` displays study minutes, sessions, check-in days and job events for the current week
- `/help-career` lists the commands

It uses a **local SQLite file** (`career_data.sqlite`) for tracking; keep and back it up. It does not read all your Discord messages or automatically infer progress from other channels. Daily check-ins are prompts; log information using slash commands. The job tally counts logged events, not necessarily distinct employers/applications. The week-1 date is **9 November 2026**.

## Install on macOS

1. **Reset any bot token you previously shared publicly.** Never paste a token into a chat, screenshot, or code file. Make sure the bot is a member of your Discord server with **Manage Channels**, **View Channels**, **Send Messages** and **Use Application Commands** permissions. Avoid granting Administrator.
2. Download and unzip this package, and open **Terminal** in the extracted folder.
3. Set up Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

4. Safely set environment variables in the **same Terminal window**:

```bash
read -s DISCORD_BOT_TOKEN
# paste the NEW token, press Enter; nothing appears while pasting
export DISCORD_BOT_TOKEN
export DISCORD_SERVER_ID="YOUR_NUMERIC_SERVER_ID"
```

5. If you have not created the channels yet, run the one-time setup first:

```bash
python setup_discord.py
```

6. **Start your ongoing bot**:

```bash
python career_bot.py
```

Leave Terminal running. In Discord, type `/help-career` or `/progress`. Commands may take a few seconds to appear after the first login. Stop with **Ctrl+C**.

## How scheduling works

The timezone is `Europe/London`, which automatically handles daylight saving transitions. Messages are deduplicated using SQLite, and sent only within the first 10 minutes of a scheduled time. If your bot is offline during that window, it **will not catch up** automatically. Your Mac must be awake and Terminal/bot running. For 24/7 operation, host the same `career_bot.py` on a reliable always-on service **with persistent storage for the SQLite database**, and store credentials in secrets/environment variables. Run **only one copy** of the bot, to avoid duplicate jobs or database conflicts.

## Data, privacy and limitations

- Anyone with access to the tracking channels can read posted study details. Use private channels/server if appropriate.
- Only totals tracked through `/study`, `/checkin`, and `/application` appear in `/progress`/Sunday reviews.
- The Sunday summary aggregates the whole server, not per-user totals.
- `/application` logs each entry as an event; it does not update an existing job's state. For now, use the channel's message threads for follow-ups.
- No automatic job searches, AI answers, streak penalties, or reminders via DMs.
- The `career_data.sqlite` file is created automatically; back it up regularly.
- Do not include confidential work material, personal visa identifiers or account passwords in Discord.

## Troubleshooting

- **Bot is not in server**: use the Developer Portal's Guild Install link to add it to Potoo Corporate Climb, and check `DISCORD_SERVER_ID` is the numeric ID, not an invite URL.
- **Slash commands absent**: check bot installed with `applications.commands` scope (typically included by Discord when bot scope is added) and that you can use application commands in the channel. Restart the bot.
- **Messages don't send**: ensure the bot has Send Messages and View Channel permissions on the channels.
- **`No module named discord`**: activate the virtualenv and `python -m pip install -r requirements.txt`.
- **Scheduled prompt missing**: verify your bot was running at the scheduled UK time; check logs, channel names and system time.
