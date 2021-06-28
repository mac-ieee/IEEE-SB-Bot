import discord
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Ping
    @commands.command(description="Pings the bot and returns the latency")
    async def ping(self, ctx):
        pingEmbed = discord.Embed(title="Ping", colour=0X2072AA)
        pingEmbed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        pingEmbed.add_field(name="Pong!", value=f"Latency: {round(self.client.latency * 1000)}ms  :ping_pong:")
        await ctx.send(embed=pingEmbed)

    # Clear
    @commands.command(aliases=["prune", "purge"])
    @commands.has_role("Exec")
    async def clear(self, ctx, arg_num=1):
        if arg_num > 1000 or arg_num < 1:
            await ctx.send(f"{ctx.author.mention}  You can only delete 1 - 1000 messages")
        else:
            await ctx.channel.purge(limit=1)
            await ctx.channel.purge(limit=arg_num)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** You need to be an **Exec** to clear messages")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** Incorrect usage")
        else:
            await ctx.send(f"{ctx.author.mention}  **UNKNOWN ERROR:** Please try again later")


def setup(client):
    client.add_cog(Utilities(client))
