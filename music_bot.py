import discord
from discord.ext import commands
import logging
import os
import asyncio
from collections import defaultdict
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('music_bot')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)

bot.guild_data = defaultdict(lambda: {
    'queue': [],
    'current_song': None,
    'voice_client': None,
    'volume': 0.5,
    'task': None,
    'permanent_channel': None,
    'check_empty_task': None
})

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synchronized {len(synced)} commands")
    except Exception as e:
        print(f"Error while synchronizing commands: {e}")

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded Cog: {filename[:-3]}")
            except Exception as e:
                print(f"Error while loading Cog {filename}: {e}")

async def main():
    await load_cogs()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("Token not found in the .env file! Make sure you have set BOT_TOKEN.")
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())