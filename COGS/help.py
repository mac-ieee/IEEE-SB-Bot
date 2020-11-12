import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx, command=None):
        # Info
        if command == "rules":
            helpEmbed = discord.Embed(description="PMs you the server's official rules", colour=0X2072AA)
        elif command == "register":
            helpEmbed = discord.Embed(
                description="Officially registers you as an IEEE Student Branch member", colour=0X2072AA)
        elif command == "chapters":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "committees":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "execteam":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        # Club Activities
        elif command == "profile":
            helpEmbed = discord.Embed(description="IN PROGRESS", colour=0X2072AA)
        elif command == "meetings":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "kudos":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        # Utilities
        elif command == "ping":
            helpEmbed = discord.Embed(description="Pings the bot and returns the latency", colour=0X2072AA)
        elif command == "clear":
            helpEmbed = discord.Embed(description="Deletes multiple messages (up to 1000).\n"
                                                  " If no value is specified, 1 message will be deleted by default."
                                      , colour=0X2072AA)
            helpEmbed.add_field(name="Usage Syntax", value="`clear <integer>`", inline=True)
            helpEmbed.add_field(name="Examples", value="`clear` \n`clear 10`", inline=True)
            helpEmbed.add_field(name="** **", value="** **", inline=False)
            helpEmbed.add_field(name="User Requirements", value="`Exec role`", inline=True)
            helpEmbed.add_field(name="Bot Permissions", value="`Manage Messages`", inline=True)
        elif command == "reminders":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "polls":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        # Moderation
        elif command == "kick":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "ban":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "unban":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "banlist":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "mute":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "unmute":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "antiswear":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        # Settings
        elif command == "changecmdprefix":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "changeavatar":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        elif command == "changestatus":
            helpEmbed = discord.Embed(description="**In Development:** Only commands with `this highlight` are working", colour=0X2072AA)
        else:
            command = "IEEE McMaster SB Bot Commands"
            helpEmbed = discord.Embed(colour=0X2072AA)
            helpEmbed.add_field(name="Info  :scroll:", value="`rules`, `register`, chapters, committees, execteam",
                                inline=False)
            helpEmbed.add_field(name="Club Activities  <:fireball:766987229713006619>",
                                value="`profile`, meetings, games",
                                inline=False)
            helpEmbed.add_field(name="Utilities  :tools:", value="`ping`, `clear`, reminders, polls", inline=False)
            helpEmbed.add_field(name="Moderation  :oncoming_police_car:",
                                value="kick, ban, unban, banlist, mute, unmute, antiswear", inline=False)
            helpEmbed.add_field(name="Settings  :gear:", value="changecmdprefix, changeavatar, changestatus",
                                inline=False)
            helpEmbed.set_footer(text="For additional information, use -help <command>")
        helpEmbed.set_author(name=f"Help: {command}")
        await ctx.send(embed=helpEmbed)


def setup(client):
    client.add_cog(Help(client))
