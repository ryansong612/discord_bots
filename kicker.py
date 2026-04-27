import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def leaderboard(ctx):
    counts = {}
    async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.member_disconnect, limit=None):
        uid = entry.user.id
        counts[uid] = counts.get(uid, 0) + entry.extra.count

    if not counts:
        await ctx.send("No disconnects found in audit log.")
        return

    top5 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = []
    for i, (user_id, count) in enumerate(top5, 1):
        user = await bot.fetch_user(user_id)
        lines.append(f"{i}. {user.name} — {count} kicks")

    await ctx.send("\n".join(lines))

@bot.command()
async def disconnects(ctx, member: discord.Member = None):
    member = member or ctx.author
    count = 0
    async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.member_disconnect, limit=None):
        if entry.user.id == member.id:
            count += entry.extra.count
    await ctx.send(f"{member.name} has force-disconnected {count} users.")

bot.run(os.environ["TOKEN"])