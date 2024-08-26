import os
import typing
import discord
from discord import app_commands
from discord.ext import commands
import json
from COGS.info import Info


class ClubActivities(commands.Cog, description="Club Activities  <:fireball:925965520610684958>"):
    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)

    @app_commands.command(name="profile", description="View your profile or the profile of your victim")
    @app_commands.describe(victim="To target a victim for their profile, use @ mentions")
    async def profile(self, ctx, victim: str = ""):
        with open("users.json", "r") as file:
            self.info.users = json.load(file)

        # Call self's profile or a victim's?
        user = None
        if victim:
            victim = victim.strip()
            if victim.startswith("<@!") and victim.endswith(">"):
                victim = victim[3:-1]

            for v in ctx.guild.members:
                if victim.lower() in str(v.nick).lower() or victim.lower() in str(v.name).lower()\
                        or victim in str(v.id):
                    victim: discord.member = v
                    break
            try:
                if str(victim.id) in self.info.users:
                    user: discord.member = victim
                else:
                    await ctx.response.send_message(f"{victim} hasn't registered yet!")
            except AttributeError:
                await ctx.response.send_message(
                    "The user you are trying to find cannot be found. Please try mentioning them directly.")
        else:
            if str(ctx.user.id) in self.info.users:
                user: discord.member = ctx.user
            else:
                await ctx.response.send_message(
                    f"Hey {ctx.user.mention}, you haven't registered yet! Type `-register` to get started")

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

    @app_commands.command(name="kill", description="Puts an engineer out of their misery")
    @app_commands.describe(victim="To target a victim to relieve, use @ mentions")
    async def kill(self, ctx, victim: discord.User = None):
        if victim and ctx.user != victim:
            await ctx.response.send_message(f"{ctx.user.mention} killed {victim.mention}")
        else:
            await ctx.response.send_message(f"{ctx.user.mention} killed themself")


async def setup(client):
    await client.add_cog(ClubActivities(client))
