import discord
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Code


def setup(client):
    client.add_cog(Info(client))
