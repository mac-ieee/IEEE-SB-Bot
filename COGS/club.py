import discord
from discord.ext import commands
import os
import json


class ClubActivities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["p", "prof"])
    async def profile(self, ctx, action=None, user_data=None):
        os.chdir(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot")
        with open("users.json", "r") as file:
            users = json.load(file)
        if str(ctx.author.id) in users:
            name = users[str(ctx.author.id)]["First Name"] + " " + users[str(ctx.author.id)]["Last Name"]
            profile_embed = discord.Embed(title=users[str(ctx.author.id)]['Title'], colour=0X2072AA)
            profile_embed.set_author(name=f"{ctx.author.name}'s Profile", icon_url=ctx.author.avatar_url)
            profile_embed.set_thumbnail(url=ctx.author.avatar_url)
            profile_embed.add_field(name="REGISTRATION INFO:",
                                    value=f"**Name:** {name}\n"
                                          f"**Email:** {users[str(ctx.author.id)]['Email']}\n"
                                          f"**Program:** {users[str(ctx.author.id)]['Program']}\n"
                                          f"**Year:** {users[str(ctx.author.id)]['Year']}",
                                    inline=True)
            profile_embed.add_field(name="COMMITTEES:",
                                    value=users[str(ctx.author.id)]['Committees'], inline=True)
            profile_embed.add_field(name="STATS:",
                                    value=f"**Level:** {users[str(ctx.author.id)]['Level']}\n"
                                          f"**EXP:** {users[str(ctx.author.id)]['Experience']}\n"
                                          f"**Coins:** {users[str(ctx.author.id)]['Coins']}",
                                    inline=False)
            await ctx.send(embed=profile_embed)
        else:
            await ctx.send(f"Hey {ctx.author.mention}, you haven't registered yet! Type `-register` to get started")




def setup(client):
    client.add_cog(ClubActivities(client))
