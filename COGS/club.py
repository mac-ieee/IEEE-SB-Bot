import os
import typing
import discord
from discord import app_commands
from discord.ext import commands
import json
import csv
import random
from COGS.info import Info


class ClubActivities(commands.Cog, description="Club Activities  <:fireball:925965520610684958>"):
    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        with open(r"Information/pokemoves.csv", "r") as file:
            pokemoves = csv.reader(file)
            self.pokemoves = list(pokemoves)[1:]

    @app_commands.command(name="profile", description="View your profile or the profile of your target")
    @app_commands.describe(target="To target a target for their profile, use @ mentions")
    async def profile(self, ctx, target: discord.User = None):
        with open("users.json", "r") as file:
            self.info.users = json.load(file)

        # Call self's profile or a target's?
        user = None
        if target:
            target = target.strip()
            if target.startswith("<@!") and target.endswith(">"):
                target = target[3:-1]

            for v in ctx.guild.members:
                if target.lower() in str(v.nick).lower() or target.lower() in str(v.name).lower()\
                        or target in str(v.id):
                    target: discord.member = v
                    break
            try:
                if str(target.id) in self.info.users:
                    user: discord.member = target
                else:
                    await ctx.response.send_message(f"{target} hasn't registered yet!")
            except AttributeError:
                await ctx.response.send_message(
                    "The user you are trying to find cannot be found. Please try mentioning them directly.")
        else:
            if str(ctx.user.id) in self.info.users:
                user: discord.member = ctx.user
            else:
                await ctx.response.send_message(
                    f"Hey {ctx.user.mention}, you haven't registered yet! Type `/register` to get started")

        user: discord.member
        if user:
            # Display Registration Info
            profile_embed = discord.Embed(title=self.info.users[str(user.id)]['Title'],
                                          description=self.info.users[str(user.id)]["About"], colour=0X2072AA)
            profile_embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar.url)
            profile_embed.set_thumbnail(url=user.avatar.url)
            profile_embed.add_field(name="REGISTRATION INFO:",
                                    value=f"**Name:** {self.info.users[str(user.id)]['Name']}\n"
                                          f"**Email:** {self.info.users[str(user.id)]['Email']}\n"
                                          f"**Program:** {self.info.users[str(user.id)]['Program']}\n"
                                          f"**Year:** {self.info.users[str(user.id)]['Year']}",
                                    inline=False)

            # Display Affiliation with Branches and the Branch Groups
            for branch in self.info.roles_list:
                group_list = ""
                guild = self.client.get_guild(int(os.getenv("GUILD_ID")))
                member = guild.get_member(ctx.user.id)
                for group_role in member.roles:
                    if group_role.name in self.info.roles_list[branch] and group_role.name != branch:
                        if isinstance(ctx.channel, discord.channel.DMChannel):
                            group_list += f"{group_role.name}\n"
                        else:
                            group_list += f"{group_role.mention}\n"
                if group_list != "":
                    profile_embed.add_field(name=branch.upper()+":", value=group_list, inline=True)

            profile_embed.add_field(name="STATS:",
                                    value=f"**Offences:** {self.info.users[str(user.id)]['Offences']}\n"
                                          f"**Level:** {self.info.users[str(user.id)]['Level']}\n"
                                          f"**EXP:** {self.info.users[str(user.id)]['Experience']}\n"
                                          f"**Coins:** {self.info.users[str(user.id)]['Coins']}",
                                    inline=False)
            await ctx.response.send_message(embed=profile_embed)

    @app_commands.command(name="pokemon", description="Start a Pokémon battle with someone!")
    @app_commands.describe(target="To target your moves on someone, use @ mentions")
    async def pokemon(self, ctx, target: discord.User = None):
        pokemoves = self.pokemoves
        random.shuffle(pokemoves)
        pokemoves
        supereff = random.randint(1,24)
        crit = random.randint(1,24)
        if supereff == 24:
            supereff = "\nIt's super effective!"
        else:
            supereff = ""
        if crit == 24:
            crit = "\nCritical hit!"
        else:
            crit = ""
        if target and ctx.user != target:
            await ctx.response.send_message(f"{ctx.user.mention} used {pokemoves[1][1]} on {target.mention}!{supereff}{crit}")
        else:
            await ctx.response.send_message(f"{ctx.user.mention} used Self-Destruct!{supereff}{crit}")


async def setup(client):
    await client.add_cog(ClubActivities(client))
