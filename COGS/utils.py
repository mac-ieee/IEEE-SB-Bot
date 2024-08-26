import typing
import discord
from discord.ext import commands
from discord import ButtonStyle, TextStyle, app_commands
from discord.ui import Button, TextInput
import json
import asyncio
from COGS.info import Info
from COGS.club import ClubActivities


class Utilities(commands.Cog, description="Utilities :tools:"):
    editable_cmds = {}

    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        self.editable_cmds = {"Profile": ClubActivities.profile}
        self.editable_cmds.update(self.info.new_cmds)

    # Ping
    @app_commands.command(name="ping", description="Pings the bot and returns the latency")
    async def ping(self, ctx):
        pingEmbed = discord.Embed(title="Ping", colour=0X2072AA)
        pingEmbed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
        pingEmbed.add_field(name="Pong!", value=f"Latency: {round(self.client.latency * 1000)}ms  :ping_pong:")
        await ctx.response.send_message(embed=pingEmbed)

    # Clear
    @app_commands.command(name="clear",
                          description="Deletes the last message")
    @app_commands.describe(num="Number of messages to delete")
    @commands.has_role("Executives")
    async def clear(self, ctx, num: int = 1):
        if num == 1:
            await ctx.channel.purge(limit=1)
            await ctx.response.send_message(f"You have deleted a message", ephemeral=True)
        if num > 1000 or num < 1:
            await ctx.response.send_message(f"You can only delete 1 - 1000 messages", ephemeral=True)
        else:
            await ctx.channel.purge(limit=int(num))
            await ctx.response.send_message(f"You have deleted {num} messages", ephemeral=True)

    
    '''@app_commands.command(name="edit", description="Edits stuff. Use `-edit` to show a list of editables")
    @app_commands.describe(cat="Choose a category", group="test", leader="test")
    async def edit(self, ctx, cat: typing.Literal["profile", "chapter", "committee"],
                   group: typing.Literal["profile", "chapter", "committee"], *, leader: str=""):
        with open(r"Information/roles_list.json", "r") as file:
            self.info.roles_list = json.load(file)'''

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.response.send_message(
                f"{ctx.author.mention}  **ERROR:** You need to be an **Executives** to clear messages")
        elif isinstance(error, commands.BadArgument):
            await ctx.response.send_message(f"{ctx.user.mention}  **ERROR:** Incorrect usage")
        else:
            await ctx.response.send_message(f"{ctx.user.mention}  **UNKNOWN ERROR:** Please try again later")


async def setup(client):
    await client.add_cog(Utilities(client))
