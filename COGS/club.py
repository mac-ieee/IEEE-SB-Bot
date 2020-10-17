import discord
from discord.ext import commands


class ClubActivities(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Code


def setup(client):
    client.add_cog(ClubActivities(client))
