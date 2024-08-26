import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

class MyClient(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix="-", case_insensitive=True)

    async def on_ready(self):
        await self.wait_until_ready()
        sync = await client.tree.sync()
        print("My boty is ready")
        print(f"Synced {len(sync)} commands")


    async def setup_hook(self):
        print("Setting up...")
        await self.load_extension("COGS.club")
        await self.load_extension("COGS.info")
        await self.load_extension("COGS.test")
        await self.load_extension("COGS.utils")

client = MyClient()


load_dotenv(".env")
client.run(os.getenv("DISCORD_TOKEN"))
