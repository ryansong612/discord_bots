import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import sqlite3
import os

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# SQLite setup
conn = sqlite3.connect("/data/kicks.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS kicks (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)")
conn.commit()

def get_count(user_id):
    cursor.execute("SELECT count FROM kicks WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def increment(user_id):
    cursor.execute("INSERT INTO kicks (user_id, count) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET count = count + 1", (user_id,))
    conn.commit()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None or after.channel is not None:
        return

    await discord.utils.sleep_until(datetime.now(timezone.utc) + timedelta(seconds=1))

    async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_disconnect, limit=5):
        age = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
        if age < 5:
            increment(member.id)
            print(f"{member.name} was force-disconnected. Total: {get_count(member.id)}")
            break

@bot.command()
async def leaderboard(ctx):
    cursor.execute("SELECT user_id, count FROM kicks ORDER BY count DESC LIMIT 5")
    rows = cursor.fetchall()

    if not rows:
        await ctx.send("无人被飞")
        return

    lines = []
    for i, (user_id, count) in enumerate(rows, 1):
        user = await bot.fetch_user(user_id)
        lines.append(f"{i}. {user.name} — {count} 航次")

    await ctx.send("\n".join(lines))

@bot.command()
async def disconnects(ctx, member: discord.Member = None):
    member = member or ctx.author
    count = get_count(member.id)
    await ctx.send(f"{member.name} 被踢飞了 {count} 次.")

bot.run(os.environ["TOKEN"])