# AI & Data Engineering Career HQ — Discord setup

This creates **7 categories, 23 text channels**, and useful starter messages.
It is safe to re-run: existing categories/channels are kept; no channels are deleted or overwritten.

## One-time preparation
1. In Discord, click **+ Add a Server → Create My Own**. Name it **AI & Data Career HQ** (or whatever you like). Keep it private and avoid sharing invite links.
2. In Discord **User Settings → Advanced**, enable Developer Mode. Right-click your new server icon and select **Copy Server ID**.
3. At https://discord.com/developers/applications, select **New Application** and create an app named **Career HQ Setup**. On the **Bot** page, create/reset the bot token if necessary. **Keep the token secret. Never paste it into ChatGPT.**
4. In the application settings under **OAuth2 → URL Generator**, select the **bot** scope and the **Manage Channels, View Channels, Send Messages** permissions (optionally **Read Message History**). Open the generated URL to add the bot to your newly created server. Do **not** give it Administrator unless you have an independent reason.
5. Install Python 3.10+ and run `python -m pip install -r requirements.txt` in this folder.
6. Set your environment variables and run the script:

**macOS / Linux:**
```bash
export DISCORD_BOT_TOKEN='your_bot_token'
export DISCORD_SERVER_ID='your_server_id'
python setup_discord.py
```
**PowerShell:**
```powershell
$env:DISCORD_BOT_TOKEN='your_bot_token'
$env:DISCORD_SERVER_ID='your_server_id'
python setup_discord.py
```

The setup will create channels and starter templates. It won't configure automatic Discord notifications or recurring reminders; post using the templates, or configure a separate scheduling bot later. After running, you may remove the setup bot from your server if you wish.

## Suggested operating rhythm
- Monday: post your main outcome in `#weekly-goals`.
- Study days: make a 30-second post in `#daily-check-in` and record your work in `#study-log`.
- When you build: post milestones in `#document-intelligence` or another project channel.
- When applying: post one entry per role in `#applications-tracker` and keep updates in its thread.
- Sunday: fill in `#weekly-review`, including applications and mock-interview outcomes.

## Important
Do not post confidential work material, employer documents, production tokens, passwords or personal immigration document numbers. Use public or synthetic documents for your portfolio.
