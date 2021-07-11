import discord
from discord.ext import commands
import os
import json
import asyncio


class Info(commands.Cog, description="Info :scroll:"):
    users = {}
    roles_list = {}
    new_cmds = {}

    def __init__(self, client):
        self.client = client
        with open("users.json", "r") as file:
            self.users = json.load(file)
        with open(r"Information/roles_list.json", "r") as file:
            self.roles_list = json.load(file)

        cmds = self.get_commands()
        cmd_names = [cmd.name.lower() for cmd in cmds]
        for branch in self.roles_list:
            if "".join(branch.lower().split()) in cmd_names:
                self.new_cmds[branch] = cmds[cmd_names.index("".join(branch.lower().split()))]
            else:
                print(f"\033[93m Warning: {branch} from roles_list has not been declared as a command")

        print("test")

    '''
    @Author: Evan C. Tanudjaja      @Date: 2021-07-10
    Displays an edit profile embed given from the userID parameter and returns the True if the command was terminated.
    May also receive a specific profile parameter to edit.
    @Params: discord.ext.commands.context.Context, str, str     @Return: bool
    '''
    async def edit_prof(self, ctx, user, param=None):
        async def get_reg_info(param_editor):
            reg_info = ""
            for p2 in prof_templ:
                if param == p2:
                    reg_info += f"**{p2}:** {str(self.users[user][param]).join(param_editor)}\n"
                else:
                    reg_info += f"**{p2}:** {self.users[user][p2]}\n"
            edit_embed.set_field_at(index=0, name="REGISTRATION INFO:", value=reg_info, inline=False)

        async def timeout():
            print("Someone took too long to respond")
            edit_embed.set_footer(text="No response received. COMMAND TERMINATED.")
            await get_reg_info(["", ""])
            await message.edit(embed=edit_embed)

        prof_templ = {
            "Name": "<Enter First & Last Names>",
            "Email": "<Enter MAC Email>",
            "Program": "<Enter Program Name>",
            "Year": "<Enter Program Year>",
            "About": "<Empty>"
        }
        with open("users.json", "r") as file:
            self.users = json.load(file)

        # Activate Registration Process if user not registered
        if str(ctx.invoked_with) == "register":
            self.users[user] = prof_templ
            edit_list = prof_templ
        else:
            # Checks if user wants a specific profile parameter to be edited
            if param:
                edit_list = {param: prof_templ[param]}
            else:
                edit_list = prof_templ

        # Init embed
        edit_embed = discord.Embed(colour=0X2072AA)
        edit_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        edit_embed.add_field(name="REGISTRATION INFO:", value="-", inline=False)
        await get_reg_info(["", ""])
        message = await ctx.send(embed=edit_embed)

        # If no specific profile parameter is indicated, then every profile parameter will be edited
        for param in edit_list:
            cancel_save = True
            # Loop profile parameter editing if user cancels on saving. Maybe they made a typo.
            while cancel_save:
                await message.remove_reaction("💾", ctx.author)
                await message.remove_reaction("❌", ctx.author)
                await get_reg_info(["```fix\n", "\n```"])
                await message.edit(embed=edit_embed)

                await message.add_reaction(emoji="💾")
                await message.add_reaction(emoji="❌")

                bad_response = True
                while bad_response:
                    # Get user response. Reaction or message?
                    done, pending = await asyncio.wait([
                        self.client.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60),
                        self.client.wait_for("reaction_add",
                                             check=lambda r, u: str(r.emoji) in ["💾", "❌"] and u == ctx.author,
                                             timeout=61)
                    ], return_when=asyncio.FIRST_COMPLETED)

                    try:
                        payload = done.pop().result()
                    except asyncio.exceptions.TimeoutError:
                        await timeout()
                        for future in pending:
                            future.cancel()
                        return True
                    else:
                        for future in pending:
                            future.cancel()

                        # Check response type
                        if type(payload) == tuple:
                            rxn, usr = payload
                            # Save reaction continues editing process, if more edits are queue
                            if str(rxn.emoji) == "💾":
                                edit_embed.set_footer(text=f"No changes were made to {param}.")
                                await get_reg_info(["", ""])
                                await message.edit(embed=edit_embed)
                                cancel_save, bad_response = False, False
                            # Terminates Command
                            elif str(rxn.emoji) == "❌":
                                edit_embed.set_footer(text="COMMAND TERMINATED.")
                                await get_reg_info(["", ""])
                                await message.edit(embed=edit_embed)
                                return True
                        elif type(payload) == discord.message.Message:
                            if param == "Name":
                                if " " not in payload.content.strip():
                                    edit_embed.set_footer(text="ERROR: Last name not found!")
                                    break
                                payload.content = payload.content.title()
                            elif param == "Email" and not payload.content.endswith("@mcmaster.ca"):
                                edit_embed.set_footer(text="ERROR: Email not found! Expected MAC Email.")
                                break
                            elif param == "Year":
                                if not payload.content.isdigit():
                                    edit_embed.set_footer(text="ERROR: Unknown year! Expected integer.")
                                    break
                                payload.content = int(payload.content)

                            bad_response = False
                            edit_embed.set_footer(text=f"Save changes to {param}?")
                            await get_reg_info(["```diff\n- ", f"\n+ {payload.content.strip()}\n```"])
                            await message.edit(embed=edit_embed)

                            # Get reaction
                            try:
                                rxn, usr = await self.client.wait_for(
                                    "reaction_add", check=lambda r, u: str(r.emoji) in ["💾", "❌"] and u == ctx.author,
                                    timeout=60)
                            except asyncio.exceptions.TimeoutError:
                                await timeout()
                                return True
                            else:
                                # Saves the response to file
                                if str(rxn.emoji) == "💾":
                                    self.users[user][param] = payload.content
                                    edit_embed.set_footer(text=f"Changes made to {param} saved successfully.")
                                    cancel_save = False
                                # Does nothing, loops the editing for the same profile parameter
                                elif str(rxn.emoji) == "❌":
                                    edit_embed.set_footer()
        return False

    async def sync_roles(self, ctx):
        with open(r"Information/roles_list.json", "r") as file:
            self.roles_list = json.load(file)

        for branch in self.roles_list:
            for group in self.roles_list[branch]:
                if group not in str(ctx.guild.roles):
                    await ctx.guild.create_role(
                        name=group, permissions=ctx.guild.default_role.permissions, hoist=True,
                        reason="Guild Role Not Found")

    async def disp_branches(self, ctx, branch, group):
        if group:
            await self.disp_groups(ctx, branch, group)
        else:
            num_groups = 0
            groups_embed = discord.Embed(title=f"List of {branch}s", colour=0X2072AA)
            groups_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            groups_embed.set_footer(text=f"For more information, use -{branch} <{branch} type>")
            for group in self.roles_list[branch]:
                groups_embed.add_field(
                    name=f"{group}  {self.roles_list[branch][group]['Logo']}",
                    value=self.roles_list[branch][group]["Description"], inline=False)
                num_groups += 1
            if num_groups == 1:
                await self.disp_groups(ctx, branch, branch)
            else:
                await ctx.send(embed=groups_embed)

    async def disp_groups(self, ctx, branch, group):
        # Filter Group
        for g in self.roles_list[branch]:
            if group.lower() in g.lower():
                group = g

        try:
            # Group Info
            group_embed = discord.Embed(title=group, colour=0X2072AA)
            group_embed.set_footer(text=f"To join/leave {group}, type 'join' or 'leave'")
            group_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            group_embed.set_thumbnail(url=self.roles_list[branch][group]["Thumbnail"])
            leader_list = ""
            for leader in self.roles_list[branch][group]["Leaders"]:
                leader_list += f"**{leader}:** {' '.join([id.join(['<@', '>']) for id in self.roles_list[branch][group]['Leaders'][leader]['DiscordID'].split(', ')])}\n"

            if leader_list == "":
                leader_list = "None"
            group_embed.add_field(name="LEADERS:", value=leader_list)
            group_embed.add_field(name="DESCRIPTION:", value=self.roles_list[branch][group]["Description"], inline=False)
            member_list = ""
            group_role = discord.utils.get(ctx.guild.roles, name=group)
            for member in ctx.guild.members:
                if group_role in member.roles:
                    member_list += f"{member.mention} "
            if member_list == "":
                member_list = "None"
            group_embed.add_field(name="MEMBERS:", value=member_list, inline=False)
            await ctx.send(embed=group_embed)

            # Join/Leave
            response = await self.client.wait_for("message", check=lambda message: message.author == ctx.author)
            if response.content == "join":
                if self.roles_list[branch][group]["Private"] == "True":
                    await response.reply(f"You cannot join a private branch/group")
                elif group_role not in ctx.author.roles:
                    await response.reply(f"You have joined {group_role}")
                    await ctx.author.add_roles(group_role)
                else:
                    await response.reply(f"You are already in {group_role}")
            elif response.content == "leave":
                if self.roles_list[branch][group]["Private"] == "True":
                    await response.reply(f"Please contact {ctx.guild.owner.mention} to resign from {branch}")
                elif group_role in ctx.author.roles:
                    await response.reply(f"You have resigned from {group_role}")
                    await ctx.author.remove_roles(group_role)
                else:
                    await response.reply(f"You were never a part of {group_role}")
        except KeyError:
            await ctx.reply(f"The specific {branch} you were looking for cannot be resolved")

    @commands.command(description="PMs you the server's official rules")
    async def rules(self, ctx):
        rules = open(r"Information/rules.txt", "r")
        await ctx.author.send(rules.read())

    @commands.command(description="Officially registers you as an IEEE Student Branch member xD")
    async def register(self, ctx):
        with open("users.json", "r") as file:
            self.users = json.load(file)

        if str(ctx.author.id) in self.users:
            await ctx.reply("You are already registered.")
        else:
            chk_terminated = await self.edit_prof(ctx, str(ctx.author.id))
            if chk_terminated:
                await ctx.reply("You have cancelled the registration.")
                self.users.pop(str(ctx.author.id))
                return
            self.users[str(ctx.author.id)]["Title"] = "Official IEEE Member"
            self.users[str(ctx.author.id)]["Offences"] = 0
            self.users[str(ctx.author.id)]["Level"] = 1
            self.users[str(ctx.author.id)]["Experience"] = 0
            self.users[str(ctx.author.id)]["Coins"] = 500
            with open("users.json", "w") as file:
                json.dump(self.users, file, indent=4)
            await ctx.reply("You have successfully registered!")

    @commands.command(hidden=True)
    async def kill(self, ctx, victim: discord.User = None):
        if victim and ctx.author != victim:
            await ctx.send(f"{ctx.author.mention} killed {victim.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} killed themself")

    @commands.command(description="Shows the upper echelon that runs and maintains IEEE Student Branch")
    async def mainbranch(self, ctx, *, group=None):
        await self.sync_roles(ctx)
        await self.disp_branches(ctx, "Main Branch", group)

    @commands.command(description="Shows all joinable Chapters and their descriptions.",
                      aliases=["chapters", "chap", "chaps"])
    async def chapter(self, ctx, *, group=None):
        await self.sync_roles(ctx)
        await self.disp_branches(ctx, "Chapter", group)

    @commands.command(description="Shows all joinable Committees and their descriptions.",
                      aliases=["committees", "comm", "comms"])
    async def committee(self, ctx, *, group=None):
        await self.sync_roles(ctx)
        await self.disp_branches(ctx, "Committee", group)


def setup(client):
    client.add_cog(Info(client))


class InvalidNameError(Exception):
    pass


class InvalidEmailError(Exception):
    pass


class InvalidProgramError(Exception):
    pass


class ForcedInteruptError(Exception):
    pass
