import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv(".env")
client = commands.Bot(command_prefix="-")
client.remove_command("help")


@client.event
async def on_ready():
    print("My Boty is ready...")


# Reload Command
@client.command()
@commands.is_owner()
async def reload(ctx, cat):
    client.unload_extension(f"COGS.{cat}")
    client.load_extension(f"COGS.{cat}")
    await ctx.send(f"{cat} reloaded successfully")


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Only the bot owner may use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Missing Argument")
    else:
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Reloading failed")


# Catch Command Errors
@client.event
async def on_command_error(ctx, error):
    pass


# Start
for filename in os.listdir("./COGS"):
    if filename.endswith(".py"):
        client.load_extension(f"COGS.{filename[:-3]}")

client.run(os.getenv("DISCORD_TOKEN"))