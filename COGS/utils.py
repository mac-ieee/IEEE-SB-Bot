import asyncio
import discord
from discord.ext import commands
import json
from COGS.info import Info
from COGS.club import ClubActivities


class Utilities(commands.Cog, description="Utilities :tools:"):
    editable_cmds = {}

    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        self.editable_cmds = {"Profile": ClubActivities.profile}
        self.editable_cmds.update(self.info.new_cmds)

    async def winedit(self, ctx, cat, group=None, leader=None):
        with open("users.json", "r") as file:
            users = json.load(file)

        if cat == "Profile":
            user = str(ctx.author.id)
            edit_embed = discord.Embed(title="Edit Profile - Name",
                                       description=users[user]["Description"], colour=0X2072AA)
            edit_embed.set_author(name=f"{ctx.author.name}'s Profile", icon_url=ctx.author.avatar_url)
            edit_embed.set_thumbnail(url=ctx.author.avatar_url)
            edit_embed.set_footer(text="Please enter your first and last name")
            edit_embed.add_field(name="REGISTRATION INFO:",
                                 value=f"**Name:** ```fix\n{users[user]['First Name']}"
                                       f" {users[user]['Last Name']}```\n"
                                       f"**Email:** {users[user]['Email']}\n"
                                       f"**Program:** {users[user]['Program']}\n"
                                       f"**Year:** {users[user]['Year']}", inline=False)
            message = await ctx.send(embed=edit_embed)

            await message.add_reaction(emoji="💾")
            await message.add_reaction(emoji="❌")
            try:
                done, pending = await asyncio.wait([
                    self.client.wait_for("message", check=lambda m: m.author == ctx.author, timeout=300),
                    self.client.wait_for("reaction_add",
                                         check=lambda r, ur: str(r.emoji) in ["💾", "❌"] and ur == ctx.author,
                                         timeout=300)
                ], return_when=asyncio.FIRST_COMPLETED)
            except TimeoutError:
                print("Someone took too long for a response")
            else:
                payload = done.pop().result()
                if type(payload) == tuple:
                    rxn, usr = payload
                    if str(rxn.emoji) == "💾":
                        edit_embed.set_footer(text="No changes were made to Name")
                        edit_embed.set_field_at(index=0, name="REGISTRATION INFO",
                                                value=f"**Name:** {users[user]['First Name']} {users[user]['Last Name']}\n"
                                                      f"**Email:** {users[user]['Email']}\n"
                                                      f"**Program:** {users[user]['Program']}\n"
                                                      f"**Year:** {users[user]['Year']}", inline=False)
                        await message.edit(embed=edit_embed)
                    elif str(rxn.emoji) == "❌":
                        edit_embed.set_footer(text="COMMAND TERMINATED")
                        edit_embed.set_field_at(index=0, name="REGISTRATION INFO",
                                                value=f"**Name:** {users[user]['First Name']} {users[user]['Last Name']}\n"
                                                      f"**Email:** {users[user]['Email']}\n"
                                                      f"**Program:** {users[user]['Program']}\n"
                                                      f"**Year:** {users[user]['Year']}", inline=False)
                        await message.edit(embed=edit_embed)
                elif type(payload) == discord.message.Message:
                    edit_embed.set_field_at(index=0, name="REGISTRATION INFO",
                                            value=f"**Name:** ```diff\n- {users[user]['First Name']}"
                                                  f" {users[user]['Last Name']}\n+ {payload.content}```\n"
                                                  f"**Email:** {users[user]['Email']}\n"
                                                  f"**Program:** {users[user]['Program']}\n"
                                                  f"**Year:** {users[user]['Year']}", inline=False)
                    await message.edit(embed=edit_embed)
                else:
                    print(payload)

                for future in pending:
                    future.cancel()
        else:
            response = await self.client.wait_for(
                "message", check=lambda message: message.author == ctx.author, timeout=300)
            self.editable_cmds[cat].description = response.content

    # Ping
    @commands.command(description="Pings the bot and returns the latency")
    async def ping(self, ctx):
        pingEmbed = discord.Embed(title="Ping", colour=0X2072AA)
        pingEmbed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        pingEmbed.add_field(name="Pong!", value=f"Latency: {round(self.client.latency * 1000)}ms  :ping_pong:")
        await ctx.send(embed=pingEmbed)

    # Clear
    @commands.command(aliases=["prune", "purge"],
                      description="Deletes multiple messages (up to 1000).\n"
                                  "If no value is specified, 1 message will be deleted by default.",
                      usage="<integer>",
                      brief="clear\nclear 10",
                      help="User: Exec Role\nBot: Manage Messages")
    @commands.has_role("Exec")
    async def clear(self, ctx, arg_num=1):
        if arg_num > 1000 or arg_num < 1:
            await ctx.send(f"{ctx.author.mention}  You can only delete 1 - 1000 messages")
        else:
            await ctx.channel.purge(limit=1)
            await ctx.channel.purge(limit=arg_num)

    @commands.command()
    async def edit(self, ctx, cat=None, group=None, *, leader=None):
        indexed_info = self.info.roles_list
        indexed_info.update({"Profile": {
            "Name": None, "Email": None, "Program": None, "Year": None, "Description": None}})
        if cat:
            # Filter cat with indexed list
            for c in self.editable_cmds:
                if cat.lower() in c.lower() or cat.lower() in self.editable_cmds[c].aliases:
                    cat = c
                    break

            if group:
                # Filter groups
                for g in self.info.roles_list[cat]:
                    if group.lower() in g.lower():
                        group = g
                        break

                if leader:
                    # Filter leaders
                    for l in self.info.roles_list[cat][group]["Leaders"]:
                        if leader.lower() in l.lower():
                            leader = l
                            break

                    await self.winedit(ctx, cat, group, leader)
                else:
                    await self.winedit(ctx, cat, group)
            else:
                await self.winedit(ctx, cat)
        else:
            edit_embed = discord.Embed(title="Edit Options", description="", colour=0X2072AA)
            await ctx.send(embed=edit_embed)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** You need to be an **Exec** to clear messages")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** Incorrect usage")
        else:
            await ctx.send(f"{ctx.author.mention}  **UNKNOWN ERROR:** Please try again later")


def setup(client):
    client.add_cog(Utilities(client))
