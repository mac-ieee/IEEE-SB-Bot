import discord
from discord.ext import commands
from COGS.info import Info
import json


class Settings(commands.Cog, description="Settings :gear:"):
    rr_channels = {}
    role_ids = []

    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        with open(r"Information/rr_channels.json", "r") as file:
            self.rr_channels = json.load(file)

    @commands.command(aliases=["br"],
                      description="Toggles reaction roles for the current channel.",
                      help="User: Executives Role\nBot: Highest Role Possible")
    @commands.has_role("Executives")
    async def br_setup(self, ctx):
        # Compare current channel with the set channel
        channel = ctx.channel.id
        stored_channel = self.rr_channels["Chapter"]["ChannelID"]
        if channel == stored_channel:
            # Disable RR
            self.rr_channels["Chapter"]["ChannelID"] = ""
            with open(r"Information/rr_channels.json", "w") as file:
                json.dump(self.rr_channels, file, indent=4)
        else:
            # Enable RR for the new Channel
            self.rr_channels["Chapter"]["ChannelID"] = channel
            with open(r"Information/rr_channels.json", "w") as file:
                json.dump(self.rr_channels, file, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        pass

def setup(client):
    client.add_cog(Settings(client))

