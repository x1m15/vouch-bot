import os
import time
import json
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import ui
from datetime import datetime, timezone 
import colorama
from colorama import Fore, Style
import asyncio
import threading
import random

g = Fore.GREEN
r = Fore.RED
b = Fore.BLUE
c = Fore.CYAN
m = Fore.MAGENTA
y = Fore.YELLOW
re = Style.RESET_ALL
dim = Style.DIM

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

banner = f"""{c}
____   ____                  .__      ___.           __   
\   \ /   /___  __ __   ____ |  |__   \_ |__   _____/  |_ 
 \   Y   /  _ \|  |  \_/ ___\|  |  \   | __ \ /  _ \   __\ 
  \     (  <_> )  |  /\  \___|   Y  \  | \_\ (  <_> )  |  
   \___/ \____/|____/  \___  >___|  /  |___  /\____/|__|  
                           \/     \/       \/                                                                
"""

def load_json_safe(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            f.write("[]")
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        with open(path, "w") as f:
            f.write("[]")
        return []

@bot.event
async def on_ready():
    global queue_EmbedMessage  
    os.system('cls')
    print(banner)
    await bot.change_presence(activity=discord.Streaming(url="https://discord.gg/", name=f"Vouch Bot"))

    try:
        synced = await bot.tree.sync()
        for app_command in synced:
            print(f"{m}{datetime.now().strftime('%H:%M:%S')}{re} | Loaded command: {c}/{app_command.name}{re}")
    except Exception as e:
        print(e)

    print(f"{m}{datetime.now().strftime('%H:%M:%S')}{re} | Logged in as: {c}{bot.user}")
    print()

@bot.tree.command(name="vouch", description="Submit a vouch")
@app_commands.describe(message="Your feedback message", stars="Your rating (1-5 stars)")
@app_commands.choices(stars=[
    app_commands.Choice(name="⭐", value=1),
    app_commands.Choice(name="⭐⭐", value=2),
    app_commands.Choice(name="⭐⭐⭐", value=3),
    app_commands.Choice(name="⭐⭐⭐⭐", value=4),
    app_commands.Choice(name="⭐⭐⭐⭐⭐", value=5)
])
async def vouch(interaction: discord.Interaction, message: str, stars: int):

    rating = "⭐" * stars

    embed = discord.Embed(
        title="Thanks for your vouch!",
        description=f"{rating}",
        color=discord.Color.og_blurple()
    )
    embed.add_field(name='Vouch:', value=f"{message}", inline=False)
    embed.add_field(name='Vouched by:', value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name='Vouched at:', value=f"{datetime.now(timezone.utc)}", inline=True)

    embed.set_author(name="Vouch Bot")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.defer()
    sent_message = await interaction.followup.send(embed=embed)

    emoji = "✅"
    try:
        await sent_message.add_reaction(emoji)
    except discord.HTTPException as e:
        print(f"Failed to add reaction: {e}")

    vouch_data = {
        "user_id": interaction.user.id,
        "user_name": str(interaction.user),
        "rating": rating,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    data = load_json_safe("vouch_data.json")
    data.append(vouch_data)

    with open("vouch_data.json", "w") as file:
        json.dump(data, file, indent=4)

@bot.tree.command(name="restore_vouches", description="Restore all vouches into this channel")
async def restore_vouches(interaction: discord.Interaction):
    channel = interaction.channel  
    data = load_json_safe("vouch_data.json")

    if not data:
        await interaction.response.send_message("No vouches found to restore.")
        return

    await interaction.response.send_message("Restoring all vouches...")

    for vouch in data:
        print(f"{m}{datetime.now().strftime('%H:%M:%S')}{re} | Restored vouch | User{dim} >>{re} {c}{vouch['user_name']}")

        embed = discord.Embed(
            title="Restored Vouch",
            description=f"{vouch['rating']}",
            color=discord.Color.og_blurple()
        )
        embed.add_field(name='Vouch:', value=f"{vouch['message']}", inline=False)
        embed.add_field(name='Vouched by:', value=f"<@{vouch['user_id']}>", inline=True)
        embed.add_field(name='Vouched at:', value=f"{vouch['timestamp']}", inline=True)

        embed.set_author(name="Vouch Bot")

        try:
            await channel.send(embed=embed)
        except discord.HTTPException as e:
            print(f"Failed to send embed: {e}")

bot.run(os.getenv("bot_token"))
