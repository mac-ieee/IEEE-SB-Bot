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

    @commands.command(description="Edits stuff. Use `-edit` to show a list of editables",
                      usage="<profile> <profile parameter>",
                      brief="profile\nprofile name",
                      help="Bot: Manage Messages")
    async def edit(self, ctx, cat=None, group=None, *, leader=None):
        with open(r"Information/roles_list.json", "r") as file:
            self.info.roles_list = json.load(file)

        indexed_info = self.info.roles_list
        indexed_info.update({"Profile": {
            "Name": None, "Email": None, "Program": None, "Year": None, "About": None}})
        if cat:
            # Filter cat with indexed list
            for c in self.editable_cmds:
                if cat.lower() in c.lower() or cat.lower() in self.editable_cmds[c].aliases:
                    cat = c
                    break
                return await ctx.reply(f"{cat} cannot be resolved. Please use `-edit` for a list of editables")
            if group:
                # Filter groups
                for g in self.info.roles_list[cat]:
                    if group.lower() in g.lower():
                        group = g
                        break
                    return await ctx.reply(
                        f"{cat}{group} cannot be resolved. Please use `-edit` for a list of editables")
                if leader:
                    # Filter leaders
                    for l in self.info.roles_list[cat][group]["Leaders"]:
                        if leader.lower() in l.lower():
                            leader = l
                            break
                    return await ctx.reply(
                        f"{cat}{group}{leader} cannot be resolved. Please use `-edit` for a list of editables")

            if cat == "Profile":
                with open("users.json", "r") as file:
                    self.info.users = json.load(file)

                if str(ctx.author.id) in self.info.users:
                    await self.info.edit_prof(ctx, str(ctx.author.id), group)
                    await ctx.reply("Profile changes made successfully.")
                    with open("users.json", "w") as file:
                        json.dump(self.info.users, file, indent=4)
                else:
                    await ctx.reply("You don't have a profile yet. Type `-register` to get started.")

            elif cat in self.info.roles_list:
                print(f"{cat = }, {group = }, {leader = }")

        else:
            profile_params = f"\n\t".join([f"- {param}" for param in indexed_info['Profile']])
            desc = f"```fix\nProfile:\n\t{profile_params}\n```"
            edit_embed = discord.Embed(title="Edit Options", description=desc, colour=0X2072AA)
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
