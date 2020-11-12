import discord
from discord.ext import commands
import os
import json
import asyncio
from COGS.info import Info, ForcedInteruptError


class ClubActivities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["p", "prof"])
    async def profile(self, ctx, action=None, data=None):
        os.chdir(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot")
        with open("users.json", "r") as file:
            users = json.load(file)
        info = Info(self.client)

        if str(ctx.author.id) in users:
            if action == "edit":
                try:
                    if data == "name":
                        names = await info.set_name(ctx, users, ctx.author)
                        users[str(ctx.author.id)]["First Name"] = names[0]
                        users[str(ctx.author.id)]["Last Name"] = names[1]
                        with open("users.json", "w") as file:
                            json.dump(users, file)
                        await ctx.send(
                            f"{ctx.author.mention}, your profile has been updated successfully!")
                    elif data == "email":
                        users[str(ctx.author.id)]["Email"] = await info.set_email(ctx, users, ctx.author)
                        with open("users.json", "w") as file:
                            json.dump(users, file)
                        await ctx.send(
                            f"{ctx.author.mention}, your profile has been updated successfully!")
                    elif data == "program":
                        users[str(ctx.author.id)]["Program"] = await info.set_program(ctx, users, ctx.author)
                        with open("users.json", "w") as file:
                            json.dump(users, file)
                        await ctx.send(
                            f"{ctx.author.mention}, your profile has been updated successfully!")
                    elif data == "year":
                        users[str(ctx.author.id)]["Year"] = await info.set_year(ctx, users, ctx.author)
                        with open("users.json", "w") as file:
                            json.dump(users, file)
                        await ctx.send(
                            f"{ctx.author.mention}, your profile has been updated successfully!")
                    else:
                        await ctx.send(
                            f"{ctx.author.mention}, what are you exactly trying to edit?")
                except asyncio.TimeoutError:
                    return await ctx.send(
                        f"Sorry {ctx.author.mention}, you took to long to respond. Command Terminated.")
                except ForcedInteruptError:
                    return await ctx.send(f"{ctx.author.mention} terminated the command")
            else:
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
