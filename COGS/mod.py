import discord
from discord.ext import commands
import os
import json
from main import temp_users
from COGS.utils import Utilities


class Moderation(commands.Cog, description="Moderation :oncoming_police_car:"):
    swear_dictionary = None

    def __init__(self, client):
        self.client = client
        self.swear_dictionary = open(
            r"Information/swear_dictionary.txt", "r")

    @commands.Cog.listener()
    async def on_message(self, msg):
        """
        self.swear_dictionary.seek(0)
        for swear in self.swear_dictionary.readlines():
            if swear.strip().lower() in msg.content.lower() and not msg.author.bot:
                await msg.channel.purge(limit=1)

                with open("users.json", "r") as file:
                    users = json.load(file)

                if str(msg.author.id) in users:
                    users[str(msg.author.id)]["Offences"] += 1
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
                    await msg.channel.send(f"{msg.author.mention}, you can't say that"
                                           f" [{users[str(msg.author.id)]['Offences']}/3]")

                    try:
                        if users[str(msg.author.id)]["Offences"] >= 3:
                            await msg.author.ban(reason="Inappropriate Behaviour")
                            await msg.channel.send(f"{msg.author} has been banned")
                            users[str(msg.author.id)]["Offences"] = 0
                            with open("users.json", "w") as file:
                                json.dump(users, file, indent=4)
                    except discord.Forbidden:
                        await msg.channel.send("**ERROR:**  My permissions are not high enough to ban this user")
                elif str(msg.author.id) in temp_users:
                    temp_users[str(msg.author.id)]["Offences"] += 1
                    await msg.channel.send(f"{msg.author.mention}, you can't say that"
                                           f" [{temp_users[str(msg.author.id)]['Offences']}/3]")

                    try:
                        if temp_users[str(msg.author.id)]["Offences"] >= 3:
                            await msg.author.ban(reason="Inappropriate Behaviour")
                            await msg.channel.send(f"{msg.author} has been banned")
                            temp_users[str(msg.author.id)]["Offences"] = 0
                    except discord.Forbidden:
                        await msg.channel.send("**ERROR:**  My permissions are not high enough to ban this user")
                else:
                    temp_users[str(msg.author.id)] = {}
                    temp_users[str(msg.author.id)]["Offences"] = 1
                    await msg.channel.send(f"{msg.author.mention}, you can't say that"
                                           f" [{temp_users[str(msg.author.id)]['Offences']}/3]")
                break
        """
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

    @commands.command(hidden=True)
    async def die(self, ctx):
        await Utilities.ping(self, ctx)

def setup(client):
    client.add_cog(Moderation(client))
