import discord
from discord.ext import commands


class Settings(commands.Cog, description="Settings :gear:"):
    def __init__(self, client):
        self.client = client

    # Code


def setup(client):
    client.add_cog(Settings(client))

