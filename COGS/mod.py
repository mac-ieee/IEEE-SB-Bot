import discord
from discord.ext import commands
import os
import json
from COGS.utils import Utilities


class Moderation(commands.Cog, description="Moderation :oncoming_police_car:"):
    swear_dictionary = None

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if "prepare for trouble" in msg.content.strip().lower():
            await msg.channel.send("AND MAKE IT DOUBLE!")
        elif "to protect the world from devastation" in msg.content.strip().lower():
            await msg.channel.send("TO UNITE ALL PEOPLE WITHIN OUR NATION")
        elif "to denounce the evils of truth and love" in msg.content.strip().lower():
            await msg.channel.send("TO EXTEND OUR REACH TO THE STARS ABOVE")
        elif "jessie" in msg.content.strip().lower():
            await msg.channel.send("JAMES!")
        elif "team rocket blasts off at the speed of light" in msg.content.strip().lower():
            await msg.channel.send("SURRENDER NOW OR PREPARE TO FIGHT")
        elif "ehe" in msg.content.strip().lower() and not msg.author.bot:
            await msg.reply("\"EHE\", TE NANDAYO?!", mention_author=True)
        elif "omae wa mou shindeiru" in msg.content.strip().lower() and not msg.author.bot:
            await msg.reply("NANI?!", mention_author=True)


async def setup(client):
    await client.add_cog(Moderation(client))
