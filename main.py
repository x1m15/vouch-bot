import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot
bot = commands.Bot(command_prefix="$", intents=intents)


# ============= JSON SAFE LOADER ==================
def load_json_safe(path: str):
    """Load JSON safely and auto-create file if missing/corrupt."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            f.write("[]")
        return []

    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        with open(path, "w") as f:
            f.write("[]")
        return []


# ============= BOT READY EVENT ==================
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Streaming(
            name="Vouch Bot",
            url="https://discord.gg/"
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Slash command sync failed: {e}")

    print(f"Logged in as {bot.user}")


# ============= /VOUCH COMMAND ==================
@bot.tree.command(name="vouch", description="Submit a vouch")
@app_commands.describe(
    message="Your feedback message",
    stars="Your rating (1-5 stars)"
)
@app_commands.choices(
    stars=[
        app_commands.Choice(name="⭐", value=1),
        app_commands.Choice(name="⭐⭐", value=2),
        app_commands.Choice(name="⭐⭐⭐", value=3),
        app_commands.Choice(name="⭐⭐⭐⭐", value=4),
        app_commands.Choice(name="⭐⭐⭐⭐⭐", value=5),
    ]
)
async def vouch(interaction: discord.Interaction, message: str, stars: int):

    rating = "⭐" * stars

    embed = discord.Embed(
        title="Thanks for your vouch!",
        description=rating,
        color=discord.Color.og_blurple()
    )
    embed.add_field(name="Vouch:", value=message, inline=False)
    embed.add_field(name="Vouched by:", value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name="Vouched at:", value=str(datetime.now(timezone.utc)), inline=True)
    embed.set_author(name="Vouch Bot")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

    # Save to JSON
    vouch_data = {
        "user_id": interaction.user.id,
        "user_name": str(interaction.user),
        "rating": rating,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    data = load_json_safe("vouch_data.json")
    data.append(vouch_data)

    with open("vouch_data.json", "w") as f:
        json.dump(data, f, indent=4)


# ============= /RESTORE_VOUCHES COMMAND ==================
@bot.tree.command(name="restore_vouches", description="Restore all vouches into this channel")
async def restore_vouches(interaction: discord.Interaction):

    data = load_json_safe("vouch_data.json")

    if not data:
        await interaction.response.send_message("No vouches found.")
        return

    await interaction.response.send_message("Restoring vouches...")

    for vouch in data:
        embed = discord.Embed(
            title="Restored Vouch",
            description=vouch["rating"],
            color=discord.Color.og_blurple()
        )
        embed.add_field(name="Vouch:", value=vouch["message"], inline=False)
        embed.add_field(name="Vouched by:", value=f"<@{vouch['user_id']}>", inline=True)
        embed.add_field(name="Vouched at:", value=vouch["timestamp"], inline=True)
        embed.set_author(name="Vouch Bot")

        await interaction.channel.send(embed=embed)


# ============= BOT STARTUP ==================
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("❌ ERROR: TOKEN environment variable missing! Set it in Railway → Variables.")
else:
    bot.run(TOKEN)
