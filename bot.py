import discord
from discord.ext import commands, tasks
import asyncio
import random
import json
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv

# ============================================================
# Load tokens from .env file (NEVER hardcode tokens in code!)
# ============================================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ============================================================
# Bot setup
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ============================================================
# Data files
# ============================================================
WARNS_FILE = "warnings.json"
NOTES_FILE = "notes.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# Events
# ============================================================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"📡 Connected to {len(bot.guilds)} server(s)")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="the server | !help"
    ))

@bot.event
async def on_member_join(member):
    channel = discord.utils.find(
        lambda c: c.name in ["general", "welcome", "👋︱welcome"],
        member.guild.text_channels
    )
    if channel:
        embed = discord.Embed(
            title=f"👋 Welcome to {member.guild.name}!",
            description=f"Hey {member.mention}, glad you're here! Type `!help` to see what I can do.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument. Try `!help {ctx.command}`")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Unknown command. Type `!help` to see all commands.")

# ============================================================
# Help command
# ============================================================
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Here's everything I can do:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🎮 Fun", value="`!hello` `!joke` `!flip` `!roll` `!8ball <question>` `!roast @user`", inline=False)
    embed.add_field(name="ℹ️ Info", value="`!serverinfo` `!userinfo @user` `!ping` `!time`", inline=False)
    embed.add_field(name="📝 Notes", value="`!note add <text>` `!note list` `!note clear`", inline=False)
    embed.add_field(name="🛡️ Mod", value="`!warn @user <reason>` `!warnings @user` `!clearwarns @user` `!kick @user` `!purge <amount>`", inline=False)
    embed.set_footer(text="Made with ❤️ using discord.py")
    await ctx.send(embed=embed)

# ============================================================
# Fun commands
# ============================================================
@bot.command()
async def hello(ctx):
    greetings = [
        f"Hey {ctx.author.mention}! 👋",
        f"What's up {ctx.author.mention}! 😎",
        f"Hello there {ctx.author.mention}! 🤖",
        f"Yo {ctx.author.mention}! 🙌"
    ]
    await ctx.send(random.choice(greetings))

@bot.command()
async def joke(ctx):
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
        "I told my wife she was drawing her eyebrows too high. She looked surprised. 😲",
        "Why don't scientists trust atoms? Because they make up everything! ⚛️",
        "What do you call a fake noodle? An impasta! 🍝",
        "Why did the bicycle fall over? Because it was two-tired! 🚲",
    ]
    await ctx.send(random.choice(jokes))

@bot.command()
async def flip(ctx):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"🪙 The coin landed on... **{result}**!")

@bot.command()
async def roll(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("❌ A dice needs at least 2 sides!")
        return
    result = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a **{result}** (d{sides})")

@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str):
    responses = [
        "✅ It is certain.", "✅ Without a doubt.", "✅ Yes, definitely!",
        "✅ You may rely on it.", "🤔 Ask again later.", "🤔 Cannot predict now.",
        "❌ Don't count on it.", "❌ My sources say no.", "❌ Very doubtful."
    ]
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_purple())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(responses), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def roast(ctx, member: discord.Member):
    roasts = [
        f"{member.mention} I'd roast you, but my parents said I'm not allowed to burn trash. 🗑️",
        f"{member.mention} You're the reason they put instructions on shampoo bottles. 🧴",
        f"{member.mention} I'd explain it to you, but I left my crayons at home. 🖍️",
        f"{member.mention} You're not stupid, you just have bad luck thinking. 🧠",
    ]
    await ctx.send(random.choice(roasts))

# ============================================================
# Info commands
# ============================================================
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name}", color=member.color)
    embed.add_field(name="Display Name", value=member.display_name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def time(ctx):
    tz = pytz.timezone("America/New_York")
    now = datetime.now(tz).strftime("%I:%M %p — %B %d, %Y")
    await ctx.send(f"🕐 Current time (ET): **{now}**")

# ============================================================
# Notes system
# ============================================================
@bot.group(name="note", invoke_without_command=True)
async def note(ctx):
    await ctx.send("Usage: `!note add <text>` | `!note list` | `!note clear`")

@note.command(name="add")
async def note_add(ctx, *, text: str):
    notes = load_json(NOTES_FILE)
    uid = str(ctx.author.id)
    if uid not in notes:
        notes[uid] = []
    notes[uid].append(text)
    save_json(NOTES_FILE, notes)
    await ctx.send(f"📝 Note saved! You now have **{len(notes[uid])}** note(s).")

@note.command(name="list")
async def note_list(ctx):
    notes = load_json(NOTES_FILE)
    uid = str(ctx.author.id)
    if uid not in notes or not notes[uid]:
        await ctx.send("📭 You have no saved notes.")
        return
    embed = discord.Embed(title="📝 Your Notes", color=discord.Color.gold())
    for i, n in enumerate(notes[uid], 1):
        embed.add_field(name=f"Note {i}", value=n, inline=False)
    await ctx.send(embed=embed)

@note.command(name="clear")
async def note_clear(ctx):
    notes = load_json(NOTES_FILE)
    uid = str(ctx.author.id)
    notes[uid] = []
    save_json(NOTES_FILE, notes)
    await ctx.send("🗑️ All your notes have been cleared.")

# ============================================================
# Moderation commands
# ============================================================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason given"):
    warns = load_json(WARNS_FILE)
    uid = str(member.id)
    if uid not in warns:
        warns[uid] = []
    warns[uid].append({"reason": reason, "by": str(ctx.author), "time": str(datetime.now())})
    save_json(WARNS_FILE, warns)
    await ctx.send(f"⚠️ {member.mention} has been warned. Reason: **{reason}** (Total warnings: {len(warns[uid])})")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    warns = load_json(WARNS_FILE)
    uid = str(member.id)
    if uid not in warns or not warns[uid]:
        await ctx.send(f"✅ {member.mention} has no warnings.")
        return
    embed = discord.Embed(title=f"⚠️ Warnings for {member.name}", color=discord.Color.orange())
    for i, w in enumerate(warns[uid], 1):
        embed.add_field(name=f"Warning {i}", value=f"Reason: {w['reason']}\nBy: {w['by']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, member: discord.Member):
    warns = load_json(WARNS_FILE)
    warns[str(member.id)] = []
    save_json(WARNS_FILE, warns)
    await ctx.send(f"✅ Cleared all warnings for {member.mention}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason given"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.name} has been kicked. Reason: **{reason}**")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("❌ Please provide a number between 1 and 100.")
        return
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Deleted **{amount}** messages.")
    await asyncio.sleep(3)
    await msg.delete()

# ============================================================
# Run the bot
# ============================================================
bot.run(TOKEN)
