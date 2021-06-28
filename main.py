import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        for cog in mapping:
            await self.get_destination().send(f"{cog.qualified_name}: {[command.name for command in mapping[cog]]}")

    async def send_cog_help(self, cog):
        await self.get_destination().send(f"{cog.qualified_name}: {[command.name for command in cog.get_commands()]}")

    async def send_group_help(self, group):
        await self.get_destination().send(f"{group.name}: {[command.name for index, command in enumerate(group.commands)]}")

    async def send_command_help(self, command):
        HelpEmbed = discord.Embed(title=f"Help: {command.name}", description=command.description, colour=0X2072AA)
        if command.usage is not None:
            HelpEmbed.add_field(name="Usage Syntax", value=f"`{command.name} {command.usage}`", inline=True)
        if command.brief is not None:
            HelpEmbed.add_field(name="Examples", value=f"`{command.brief}`", inline=True)
        if command.aliases:
            aliases = ""
            for alias in command.aliases:
                aliases += f"{alias}\n"
            HelpEmbed.add_field(name="Aliases", value=f"`{aliases}`")
        if command.help is not None:
            HelpEmbed.add_field(name="Requirements", value=f"```fix\n{command.help}\n```", inline=True)
        await self.get_destination().send(embed=HelpEmbed)


load_dotenv(".env")
intents = discord.Intents.all()
client = commands.Bot(command_prefix="-", intents=intents, help_command=CustomHelpCommand())
temp_users = {}


@client.event
async def on_ready():
    print("My Boty is ready...")


async def cog_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Only the bot owner may use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Missing Argument")
    else:
        await ctx.send(f"{error}")


@client.command()
@commands.is_owner()
async def reload(ctx, cat):
    try:
        client.unload_extension(f"COGS.{cat}")
    except commands.ExtensionNotLoaded:
        pass
    try:
        client.load_extension(f"COGS.{cat}")
        await ctx.send(f"{cat} reloaded successfully")
    except commands.ExtensionNotFound:
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Extension not found")


@client.command()
@commands.is_owner()
async def unload(ctx, cat):
    try:
        client.unload_extension(f"COGS.{cat}")
        await ctx.send(f"{cat} unloaded successfully")
    except commands.ExtensionNotLoaded:
        await ctx.send(f"{ctx.author.mention}  **ERROR:** Extension already unloaded")


@reload.error
async def reload_error(ctx, error):
    await cog_error(ctx, error)


@unload.error
async def reload_error(ctx, error):
    await cog_error(ctx, error)


'''
# Catch Command Errors
@client.event
async def on_command_error(ctx, error):
    pass
'''

# Start
for filename in os.listdir("./COGS"):
    if filename.endswith(".py"):
        client.load_extension(f"COGS.{filename[:-3]}")

client.run(os.getenv("DISCORD_TOKEN"))