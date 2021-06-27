import discord
from discord.ext import commands
import json
import asyncio
from COGS.info import Info, ForcedInteruptError


class ClubActivities(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def get_profile(self, ctx, users, user):
        name = users[str(user.id)]["First Name"] + " " + users[str(user.id)]["Last Name"]
        profile_embed = discord.Embed(title=users[str(user.id)]['Title'],
                                      description=users[str(user.id)]['Description'], colour=0X2072AA)
        profile_embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar_url)
        profile_embed.set_thumbnail(url=user.avatar_url)
        profile_embed.add_field(name="REGISTRATION INFO:",
                                value=f"**Name:** {name}\n"
                                      f"**Email:** {users[str(user.id)]['Email']}\n"
                                      f"**Program:** {users[str(user.id)]['Program']}\n"
                                      f"**Year:** {users[str(user.id)]['Year']}",
                                inline=False)
        info = Info(self.client)
        for group in info.role_groups:
            group_list = ""
            for role in user.roles:
                if role.name in info.roles_list and info.roles_list[role.name]["Group"].lower() == group.lower()[0:-1]:
                    group_list += f"{role.mention}\n"
            if group_list != "":
                profile_embed.add_field(name=group.upper()+":", value=group_list, inline=True)

        profile_embed.add_field(name="STATS:",
                                value=f"**Offences:** {users[str(user.id)]['Offences']}\n"
                                      f"**Level:** {users[str(user.id)]['Level']}\n"
                                      f"**EXP:** {users[str(user.id)]['Experience']}\n"
                                      f"**Coins:** {users[str(user.id)]['Coins']}",
                                inline=False)
        await ctx.send(embed=profile_embed)

    @commands.command(aliases=["p", "prof"])
    async def profile(self, ctx, action="", data=None):
        with open("users.json", "r") as file:
            users = json.load(file)
        info = Info(self.client)

        if action.startswith("<@!") and action.endswith(">"):
            if action.lstrip("<@!").rstrip(">") in users:
                user = ctx.guild.get_member(int(action.lstrip("<@!").rstrip(">")))
                await self.get_profile(ctx, users, user)
            else:
                await ctx.reply(f"That user hasn't registered yet.")
        elif action == "edit" and str(ctx.author.id) in users:
            try:
                if data == "name":
                    names = await info.set_name(ctx, users, ctx.author)
                    users[str(ctx.author.id)]["First Name"] = names[0]
                    users[str(ctx.author.id)]["Last Name"] = names[1]
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
                    await ctx.send(
                        f"{ctx.author.mention}, your profile has been updated successfully!")
                    await ctx.author.edit(nick=names[0])
                elif data == "email":
                    users[str(ctx.author.id)]["Email"] = await info.set_email(ctx, users, ctx.author)
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
                    await ctx.send(
                        f"{ctx.author.mention}, your profile has been updated successfully!")
                elif data == "program":
                    users[str(ctx.author.id)]["Program"] = await info.set_program(ctx, users, ctx.author)
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
                    await ctx.send(
                        f"{ctx.author.mention}, your profile has been updated successfully!")
                elif data == "year":
                    users[str(ctx.author.id)]["Year"] = await info.set_year(ctx, users, ctx.author)
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
                    await ctx.send(
                        f"{ctx.author.mention}, your profile has been updated successfully!")
                elif data == "description":
                    users[str(ctx.author.id)]["Description"] = await info.set_desc(ctx, ctx.author)
                    with open("users.json", "w") as file:
                        json.dump(users, file, indent=4)
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
            except discord.Forbidden:
                return await ctx.send("**ERROR:** Cannot change discord nickname! Permissions missing or too low!")
        else:
            if str(ctx.author.id) in users:
                await self.get_profile(ctx, users, ctx.author)
            else:
                await ctx.send(f"Hey {ctx.author.mention}, you haven't registered yet! Type `-register` to get started")


def setup(client):
    client.add_cog(ClubActivities(client))
