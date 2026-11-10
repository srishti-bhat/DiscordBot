"""Potoo Corporate Climb — private study/career accountability Discord bot.

Uses Discord slash commands (no message-content privileged intent) and a local SQLite
file. Keep one instance running and preserve career_data.sqlite when redeploying.
"""
import asyncio
import logging
import os
import sqlite3
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger('potoo')
TIMEZONE = ZoneInfo('Europe/London')
BASE_DATE = date(2026, 11, 9)
DB_PATH = Path(os.environ.get('CAREER_DB_PATH', str(Path(__file__).with_name('career_data.sqlite'))))
SERVER_ID = int(os.environ['DISCORD_SERVER_ID'])
TOKEN = os.environ['DISCORD_BOT_TOKEN']

MODULES = [
    'Advanced Python', 'FastAPI, Testing and Git', 'SQL Performance and Docker',
    'Embeddings and Retrieval', 'RAG and Document Recommendations',
    'Azure AI Architecture and Reindexing', 'AI Evaluation',
    'Security and Reliability', 'Deployment and Monitoring',
    'System Design', 'Technical Interviews', 'Portfolio and Career Launch',
]


def now_uk():
    return datetime.now(TIMEZONE)


def week_number(d):
    return max(1, min(12, (d - BASE_DATE).days // 7 + 1))


def monday(d):
    return d - timedelta(days=d.weekday())


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('''CREATE TABLE IF NOT EXISTS study (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        when_uk TEXT NOT NULL, minutes INTEGER NOT NULL,
        topic TEXT NOT NULL, notes TEXT NOT NULL DEFAULT ''
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        when_uk TEXT NOT NULL, company TEXT NOT NULL, role TEXT NOT NULL,
        stage TEXT NOT NULL, next_step TEXT NOT NULL DEFAULT ''
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        when_uk TEXT NOT NULL, goal TEXT NOT NULL
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS sent (
        key TEXT PRIMARY KEY, sent_at TEXT NOT NULL
    )''')
    con.commit()
    return con


def stats(start: date, end_exclusive: date):
    with connect_db() as con:
        start_s = start.isoformat()
        end_s = end_exclusive.isoformat()
        minutes, sessions = con.execute(
            'SELECT COALESCE(SUM(minutes),0), COUNT(*) FROM study WHERE substr(when_uk,1,10)>=? AND substr(when_uk,1,10)<?',
            (start_s, end_s)).fetchone()
        applications = con.execute(
            'SELECT COUNT(*) FROM applications WHERE substr(when_uk,1,10)>=? AND substr(when_uk,1,10)<?',
            (start_s, end_s)).fetchone()[0]
        checkins = con.execute(
            'SELECT COUNT(DISTINCT substr(when_uk,1,10)) FROM checkins WHERE substr(when_uk,1,10)>=? AND substr(when_uk,1,10)<?',
            (start_s, end_s)).fetchone()[0]
    return minutes, sessions, applications, checkins


def add_event(sql, params):
    with connect_db() as con:
        con.execute(sql, params)
        con.commit()


class CareerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Guild-scoped commands are registered quickly; global registration unnecessary.
        self.tree.copy_global_to(guild=discord.Object(id=SERVER_ID))
        synced = await self.tree.sync(guild=discord.Object(id=SERVER_ID))
        LOG.info('Synced %s slash commands to server %s', len(synced), SERVER_ID)
        schedule_check.start()


bot = CareerBot()


def valid_guild(interaction: discord.Interaction):
    return interaction.guild_id == SERVER_ID


@bot.tree.command(name='checkin', description='Record one achievable study goal for today')
@app_commands.describe(goal='What is your one realistic goal today?')
async def checkin(interaction: discord.Interaction, goal: str):
    if not valid_guild(interaction):
        await interaction.response.send_message('Use this in Potoo Corporate Climb.', ephemeral=True)
        return
    add_event('INSERT INTO checkins(user_id,when_uk,goal) VALUES (?,?,?)',
              (interaction.user.id, now_uk().isoformat(), goal[:500]))
    await interaction.response.send_message('✅ Check-in saved!', ephemeral=True)
    channel = discord.utils.get(interaction.guild.text_channels, name='daily-check-in')
    if channel:
        await channel.send(f'🎯 **Daily goal — {interaction.user.mention}**\n{discord.utils.escape_mentions(goal[:500])}', allowed_mentions=discord.AllowedMentions(users=True))


@bot.tree.command(name='study', description='Log a completed study session')
@app_commands.describe(minutes='Focused time spent (1–600)', topic='What did you study?', notes='What did you build or learn?')
async def study(interaction: discord.Interaction, minutes: app_commands.Range[int,1,600], topic: str, notes: str = ''):
    if not valid_guild(interaction):
        await interaction.response.send_message('Use this in Potoo Corporate Climb.', ephemeral=True)
        return
    add_event('INSERT INTO study(user_id,when_uk,minutes,topic,notes) VALUES (?,?,?,?,?)',
              (interaction.user.id, now_uk().isoformat(), minutes, topic[:150], notes[:600]))
    await interaction.response.send_message(f'✅ Logged {minutes} focused minutes.', ephemeral=True)
    channel = discord.utils.get(interaction.guild.text_channels, name='study-log')
    if channel:
        await channel.send(f'📚 **Study log — {interaction.user.mention}**\n**{minutes} min:** {discord.utils.escape_mentions(topic[:150])}\n{discord.utils.escape_mentions(notes[:600])}', allowed_mentions=discord.AllowedMentions(users=True))


@bot.tree.command(name='application', description='Log a new application or interview-stage event')
@app_commands.describe(company='Company name', role='Job title', stage='Saved, Applied, Screen, Interview, Offer, Rejected', next_step='Next follow-up or action')
async def application(interaction: discord.Interaction, company: str, role: str, stage: str = 'Applied', next_step: str = ''):
    if not valid_guild(interaction):
        await interaction.response.send_message('Use this in Potoo Corporate Climb.', ephemeral=True)
        return
    add_event('INSERT INTO applications(user_id,when_uk,company,role,stage,next_step) VALUES (?,?,?,?,?,?)',
              (interaction.user.id, now_uk().isoformat(), company[:150], role[:150], stage[:60], next_step[:400]))
    await interaction.response.send_message('✅ Job event recorded.', ephemeral=True)
    channel = discord.utils.get(interaction.guild.text_channels, name='applications-tracker')
    if channel:
        text = (f'💼 **Job event — {interaction.user.mention}**\n**Company:** {company[:150]}\n**Role:** {role[:150]}\n'
                f'**Stage:** {stage[:60]}\n**Next:** {next_step[:400] or "Not set"}')
        await channel.send(discord.utils.escape_mentions(text).replace(discord.utils.escape_mentions(interaction.user.mention), interaction.user.mention), allowed_mentions=discord.AllowedMentions(users=True))


@bot.tree.command(name='progress', description='See tracked learning and applications this week')
async def progress(interaction: discord.Interaction):
    if not valid_guild(interaction):
        await interaction.response.send_message('Use this in Potoo Corporate Climb.', ephemeral=True)
        return
    today = now_uk().date()
    start = monday(today)
    minutes, sessions, applications, checkins = stats(start, start + timedelta(days=7))
    week = week_number(today)
    await interaction.response.send_message(
        f'📊 **Week {week}: {MODULES[week-1]}**\n'
        f'📚 {minutes} study minutes across {sessions} sessions\n'
        f'🎯 Check-ins on {checkins} days\n'
        f'💼 {applications} job events recorded\n'
        f'Current weekly target: 360–540 study minutes and 5 tailored applications.\n'
        f'_Totals count records in this server, across its users._', ephemeral=True)


@bot.tree.command(name='help-career', description='Show the career bot commands')
async def help_career(interaction: discord.Interaction):
    await interaction.response.send_message(
        '**Potoo Study Bot** 🐦\n'
        '`/checkin goal:...` — set a daily goal\n'
        '`/study minutes:... topic:... notes:...` — log completed work\n'
        '`/application company:... role:... stage:... next_step:...` — log a job event\n'
        '`/progress` — show this week’s tracked totals\n'
        'Scheduled: 08:00 daily check-in, 20:00 daily review, Sunday 19:00 weekly summary (Europe/London).',
        ephemeral=True)


async def post_once(guild: discord.Guild, date_key: str, channel_name: str, content: str):
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if channel is None:
        LOG.warning('Missing #%s; skipping %s', channel_name, date_key)
        return
    with connect_db() as con:
        if con.execute('SELECT 1 FROM sent WHERE key=?', (date_key,)).fetchone():
            return
    try:
        await channel.send(content, allowed_mentions=discord.AllowedMentions.none())
    except discord.HTTPException:
        LOG.exception('Could not send %s in #%s', date_key, channel_name)
        return
    with connect_db() as con:
        con.execute('INSERT OR IGNORE INTO sent(key,sent_at) VALUES (?,?)', (date_key, now_uk().isoformat()))
        con.commit()
    LOG.info('Sent %s', date_key)


@tasks.loop(seconds=30)
async def schedule_check():
    guild = bot.get_guild(SERVER_ID)
    if guild is None:
        LOG.warning('Bot cannot access server ID %s — invite it and verify ID', SERVER_ID)
        return
    here = now_uk()
    today = here.date()
    week = week_number(today)
    topic = MODULES[week - 1]
    # 10 minute tolerance in case the polling loop starts a little late; no backfilling after downtime.
    minute_of_day = here.hour * 60 + here.minute
    if 8*60 <= minute_of_day < 8*60+10:
        await post_once(guild, f'morning:{today}', 'daily-check-in',
            f'🌤️ **Good morning! Daily check-in — {today:%a %d %b}**\n'
            f'**Week {week}: {topic}**\n'
            '🎯 What is one realistic thing you will finish today?\n'
            '📚 Study, code, or one meaningful job-search action all count.\n'
            'Use `/checkin` to record your goal; use `/study` once you finish a session.')
    if 20*60 <= minute_of_day < 20*60+10:
        await post_once(guild, f'evening:{today}', 'daily-check-in',
            f'🌙 **Evening reflection — {today:%a %d %b}**\n'
            '✅ What did you complete? 🧱 What blocked you? ➡️ What is next?\n'
            'Log focused minutes with `/study`. Rest days are part of the plan; no guilt for missing a day.')
    if today.weekday() == 6 and 19*60 <= minute_of_day < 19*60+10:
        start = monday(today)
        mins, sessions, apps, checkins = stats(start, start + timedelta(days=7))
        await post_once(guild, f'weekly:{today}', 'weekly-review',
            f'📊 **Weekly review — {start:%d %b} to {today:%d %b}**\n'
            f'📚 **{mins}** study minutes in **{sessions}** sessions\n'
            f'🎯 Goals logged on **{checkins}** days\n'
            f'💼 **{apps}** job events recorded\n'
            '**Review:** What did you ship? What did you learn? What was difficult?\n'
            'What is your one main priority next week?')


@schedule_check.before_loop
async def before_schedule():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    LOG.info('Online as %s | Server: %s | UK time: %s', bot.user, SERVER_ID, now_uk().isoformat())


if __name__ == '__main__':
    connect_db().close()
    bot.run(TOKEN)
