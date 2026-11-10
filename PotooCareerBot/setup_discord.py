"""One-time Discord learning and career server setup.

Install: python -m pip install -r requirements.txt
Set DISCORD_BOT_TOKEN and DISCORD_SERVER_ID in your local environment.
Run: python setup_discord.py

Creates only missing categories/channels. Does not delete existing content.
"""
import os
import asyncio
import discord

CATEGORIES = [
    ("00 · START HERE", [
        ("welcome-and-roadmap", "Your 12-week AI + data engineering roadmap and server guide."),
        ("weekly-goals", "One outcome for each week; update every Sunday."),
    ]),
    ("01 · DAILY ACCOUNTABILITY", [
        ("daily-check-in", "Post today's study goal and what you completed."),
        ("study-log", "Log hours, techniques learned, blockers and next steps."),
        ("weekly-review", "What worked, what slipped, and next week's adjustments."),
        ("wins-and-milestones", "Celebrate completed projects, interviews and improvements."),
    ]),
    ("02 · LEARNING TRACKS", [
        ("python-and-apis", "Advanced Python, testing, FastAPI and clean code."),
        ("sql-and-data-engineering", "SQL tuning, pipelines, Fabric, Azure data engineering."),
        ("rag-and-azure-ai", "Embeddings, hybrid retrieval, Azure AI Search, RAG and evaluation."),
        ("cloud-devops-security", "Docker, GitHub Actions, Azure identity, CI/CD, monitoring and security."),
        ("system-design", "Scale, architecture choices, queues, caching and tradeoffs."),
    ]),
    ("03 · PORTFOLIO LAB", [
        ("document-intelligence", "Main project: RAG + document recommendation engine."),
        ("pipeline-project", "Incremental ingestion, deduplication, resilience and observability."),
        ("rag-evaluation", "Datasets, retrieval metrics, groundedness, cost and latency."),
    ]),
    ("04 · CAREER LAUNCH", [
        ("job-leads", "Glasgow hybrid AI/data roles; track salary and sponsorship."),
        ("applications-tracker", "Applications, stages, next actions and follow-up dates."),
        ("cv-and-linkedin", "CV achievements, targeted summaries and LinkedIn progress."),
        ("recruiter-outreach", "Recruiter messages, referrals and conversations."),
    ]),
    ("05 · INTERVIEW GYM", [
        ("python-sql-challenges", "Coding questions and timed problem-solving."),
        ("ai-system-design-mocks", "RAG, data pipelines, cloud architecture mock questions."),
        ("star-stories", "Leadership, ownership, reliability and stakeholder examples."),
    ]),
    ("06 · REFERENCE SHELF", [
        ("learning-resources", "Keep a short, curated list of docs and courses."),
        ("questions-and-blockers", "Capture confusing topics and troubleshoot later."),
    ]),
]

SEEDS = {
    "welcome-and-roadmap": """**Welcome to your AI + Data Engineering career HQ!** 🚀\n**Goal:** Glasgow hybrid role, £55k+, Skilled Worker sponsorship, targeting AI Engineer / Applied AI Engineer / Senior Data Engineer.\n**12-week roadmap:**\n• Weeks 1–3: advanced Python, FastAPI, tests, SQL performance, Docker\n• Weeks 4–6: search, embeddings, RAG, Azure reindexing\n• Weeks 7–9: evaluation, security, CI/CD and monitoring\n• Weeks 10–12: system design, mock interviews, CV and portfolio\n**Routine:** choose 6–9 focused hours a week, post a short daily check-in, and do a Sunday review. Start at #weekly-goals.\n**Important:** Don't share work-confidential ChatVMS code or documents here. Use synthetic or public test data.""",
    "weekly-goals": """**Weekly planning template**\n**Week number / dates:**\n**One main technical outcome:**\n**Portfolio milestone:**\n**Interview practice:**\n**Applications (target: 5 relevant):**\n**Recruiter conversations (target: 3):**\n**Definition of done:**\n**Available study hours:**""",
    "daily-check-in": """**Daily check-in template**\n📍 Today: \n🎯 One achievable goal: \n⏱️ Planned / actual focus minutes: \n✅ Completed: \n🧱 Blocker: \n➡️ Next action:""",
    "study-log": """**Study log template**\n**Date / Week:**\n**Topic:**\n**Time spent:**\n**What I built / tested:**\n**What I can explain without notes:**\n**Link to code (if public):**""",
    "weekly-review": """**Sunday review template**\n**Hours studied:**\n**Most important thing shipped:**\n**Key concept mastered:**\n**Interview problems completed:**\n**Applications / replies / interviews:**\n**What got in the way:**\n**What changes next week:**""",
    "applications-tracker": """**Job application template** (one message per role; reply in thread for updates)\n**Company / role:**\n**Location / hybrid:**\n**Salary or range:**\n**Sponsorship:** Confirmed / Unknown / No\n**URL:**\n**Date applied:**\n**CV version:** AI Engineer / Data Engineer\n**Stage:** Saved / Applied / Screen / Interview / Offer / Rejected\n**Next action + date:**\n**Contact / referral:**\n_Keep application notes here but avoid personal visa IDs._""",
    "job-leads": """**Job lead template**\nCompany — Role — Location — Salary — Hybrid days — Sponsorship evidence — Link — Deadline\nPrioritise Glasgow hybrid roles at £55k+ and check sponsorship before investing time.""",
    "star-stories": """**STAR template**\nSituation: \nTask: \nAction (my specific contribution): \nResult (evidence / metric): \nWhat I'd improve: \nStart with ChatVMS indexing reliability, Azure data pipelines, Power BI refresh reduction, mentoring and stakeholder delivery.""",
    "document-intelligence": """**Flagship project — Definition of done**\n[ ] Public/synthetic documents\n[ ] FastAPI endpoints and validated metadata\n[ ] Automated ingestion + idempotent reindex\n[ ] Keyword/vector/hybrid retrieval comparison\n[ ] RAG with cited responses\n[ ] Related-document recommendations\n[ ] Document-level permission tests\n[ ] Evaluation dataset + Recall@5 / MRR / NDCG@10\n[ ] CI/CD, logs, monitoring, architecture diagram and README""",
    "learning-resources": """**Official resources**\nPython: https://docs.python.org/3/\nFastAPI: https://fastapi.tiangolo.com/\nDocker: https://docs.docker.com/get-started/\nAzure AI Search RAG: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview\nGitHub Actions: https://docs.github.com/en/actions""",
}

class SetupBot(discord.Client):
    async def on_ready(self):
        try:
            guild_id = int(os.environ["DISCORD_SERVER_ID"])
            guild = self.get_guild(guild_id)
            if guild is None:
                raise RuntimeError("Bot is not in the server, or DISCORD_SERVER_ID is wrong.")
            me = guild.me
            if me is None or not me.guild_permissions.manage_channels:
                raise RuntimeError("The bot needs Manage Channels permission in this server.")
            print(f"Setting up {guild.name} (ID {guild.id})")
            for category_name, channels in CATEGORIES:
                category = discord.utils.get(guild.categories, name=category_name)
                if category is None:
                    category = await guild.create_category(category_name, reason="Career curriculum setup")
                    print(f"+ Category: {category_name}")
                for channel_name, topic in channels:
                    channel = discord.utils.get(guild.text_channels, name=channel_name)
                    if channel is None:
                        channel = await guild.create_text_channel(channel_name, category=category, topic=topic, reason="Career curriculum setup")
                        print(f"  + #{channel_name}")
                        if channel_name in SEEDS and channel.permissions_for(me).send_messages:
                            await channel.send(SEEDS[channel_name])
                    else:
                        print(f"  = #{channel_name} already exists (left unchanged)")
                await asyncio.sleep(0.5)
            print("Done. Review channels and optionally delete Discord's default #general manually.")
        except Exception as exc:
            print(f"Setup failed: {exc}")
        finally:
            await self.close()

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or not os.getenv("DISCORD_SERVER_ID"):
        raise SystemExit("Set DISCORD_BOT_TOKEN and DISCORD_SERVER_ID first. See README.md.")
    client = SetupBot(intents=discord.Intents.default())
    client.run(token)
