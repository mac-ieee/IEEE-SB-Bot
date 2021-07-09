import discord
from discord.ext import commands
import json
import asyncio
from COGS.info import Info, ForcedInteruptError


class ClubActivities(commands.Cog, description="Club Activities  <:fireball:766987229713006619>"):
    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)

    @commands.command(aliases=["p", "prof"])
    async def profile(self, ctx, *, victim=None):
        with open("users.json", "r") as file:
            users = json.load(file)

        # Call self's profile or a victim's?
        user = None
        if victim:
            if victim.startswith("<@!") and victim.endswith(">"):
                victim = victim[3:-1]

            for v in ctx.guild.members:
                if victim.lower() in str(v.nick).lower() or victim.lower() in str(v.name).lower() or victim in str(v.id):
                    victim: discord.member = v
                    break
            try:
                if str(victim.id) in users:
                    user: discord.member = victim
                else:
                    await ctx.reply(f"{victim} hasn't registered yet!")
            except AttributeError:
                await ctx.reply("The user you are trying to find cannot be found. Please try mentioning them directly.")
        else:
            if str(ctx.author.id) in users:
                user: discord.member = ctx.author
            else:
                await ctx.send(f"Hey {ctx.author.mention}, you haven't registered yet! Type `-register` to get started")

        if user:
            # Display Registration Info
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

            # Display Affiliation with Branches and the Branch Groups
            for branch in self.info.roles_list:
                group_list = ""
                for group_role in user.roles:
                    if group_role.name in self.info.roles_list[branch] and group_role.name != branch:
                        group_list += f"{group_role.mention}\n"
                if group_list != "":
                    profile_embed.add_field(name=branch.upper()+":", value=group_list, inline=True)

            profile_embed.add_field(name="STATS:",
                                    value=f"**Offences:** {users[str(user.id)]['Offences']}\n"
                                          f"**Level:** {users[str(user.id)]['Level']}\n"
                                          f"**EXP:** {users[str(user.id)]['Experience']}\n"
                                          f"**Coins:** {users[str(user.id)]['Coins']}",
                                    inline=False)
            await ctx.send(embed=profile_embed)

def setup(client):
    client.add_cog(ClubActivities(client))
