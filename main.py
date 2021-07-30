import discord
from discord.ext import commands
from discord_components.client import DiscordComponents
import os
from dotenv import load_dotenv


class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        help_embed = discord.Embed(title="IEEE McMaster SB Bot Command List", colour=0X2072AA)
        help_embed.set_footer(text="For additional information, use -help <command>")

        try:
            for cog in mapping:
                help_embed.add_field(name=cog.description,
                                     value="> " + "".join([f"`{command.name}`, " for command in cog.get_commands()
                                                           if not command.hidden])[:-2],
                                     inline=False)
        except AttributeError:
            pass
        await self.get_destination().send(embed=help_embed)

    async def send_cog_help(self, cog):
        await self.get_destination().send(f"{cog.qualified_name}: {[command.name for command in cog.get_commands()]}")

    async def send_group_help(self, group):
        await self.get_destination().send(
            f"{group.name}: {[command.name for index, command in enumerate(group.commands)]}")

    async def send_command_help(self, command):
        help_embed = discord.Embed(title=f"Help: {command.name}", description=command.description, colour=0X2072AA)
        if command.usage is not None:
            help_embed.add_field(name="Usage Syntax", value=f"`{command.name} {command.usage}`", inline=True)
        if command.brief is not None:
            help_embed.add_field(name="Examples", value=f"`{command.brief}`", inline=True)
        if command.aliases:
            help_embed.add_field(name="Aliases", value="".join([f"`{alias}`\n" for alias in command.aliases]))
        if command.help is not None:
            help_embed.add_field(name="Requirements", value=f"```fix\n{command.help}\n```", inline=True)
        await self.get_destination().send(embed=help_embed)


load_dotenv(".env")
intents = discord.Intents.all()
client = commands.Bot(command_prefix="-", intents=intents, help_command=CustomHelpCommand(), case_insensitive=True)
temp_users = {}


@client.event
async def on_ready():
    print("\033[0m My Boty is ready...")
    DiscordComponents(client)


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
client.load_extension(f"COGS.info")
client.load_extension(f"COGS.club")
client.load_extension(f"COGS.utils")
client.load_extension(f"COGS.mod")
client.load_extension(f"COGS.settings")
client.load_extension(f"COGS.help")

client.run(os.getenv("DISCORD_TOKEN"))
