import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

disconnect_counts = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and after.channel is None:
        uid = member.id
        disconnect_counts[uid] = disconnect_counts.get(uid, 0) + 1
        print(f"{member.name} disconnected. Total: {disconnect_counts[uid]}")

@bot.command()
async def disconnects(ctx, member: discord.Member = None):
    member = member or ctx.author
    count = disconnect_counts.get(member.id, 0)
    await ctx.send(f"{member.name} has disconnected {count} times.")

@bot.command()
async def leaderboard(ctx):
    if not disconnect_counts:
        await ctx.send("No disconnects recorded yet.")
        return

    top5 = sorted(disconnect_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    lines = []
    for i, (user_id, count) in enumerate(top5, 1):
        user = await bot.fetch_user(user_id)
        lines.append(f"{i}. {user.name} — {count} disconnects")

    await ctx.send("\n".join(lines))


if __name__ == "__main__":
    bot.run(os.environ["TOKEN"])