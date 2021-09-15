import discord
from discord.ext import commands
import discord_components.interaction
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
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
            await message.edit(embed=edit_embed, components=[])

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
        but_next = Button(style=ButtonStyle.grey, label="Next", emoji="➡")
        but_exit = Button(style=ButtonStyle.red, label="Exit", emoji="✖")
        but_save = Button(style=ButtonStyle.blue, label="Save", emoji="💾")
        but_cancel = Button(style=ButtonStyle.red, label="Cancel", emoji="✖")
        message = await ctx.send(embed=edit_embed)

        # If no specific profile parameter is indicated, then every profile parameter will be edited
        for param in edit_list:
            cancel_save = True
            # Loop profile parameter editing if user cancels on saving. Maybe they made a typo.
            while cancel_save:
                await get_reg_info(["```fix\n", "\n```"])
                await message.edit(embed=edit_embed, components=[[but_next, but_exit]])

                bad_response = True
                while bad_response:
                    # Get user response. Reaction or message?
                    done, pending = await asyncio.wait([
                        self.client.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60),
                        self.client.wait_for("button_click", check=lambda b: b.author == ctx.author)
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
                        if type(payload) == discord_components.interaction.Interaction:
                            # Save reaction continues editing process, if more edits are queue
                            if payload.component.label == "Next":
                                edit_embed.set_footer(text=f"No changes were made to {param}.")
                                await get_reg_info(["", ""])
                                await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed)

                                cancel_save, bad_response = False, False
                            # Terminates Command
                            elif payload.component.label == "Exit":
                                edit_embed.set_footer(text="COMMAND TERMINATED.")
                                await get_reg_info(["", ""])
                                await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed,
                                                      components=[])
                                return True
                        elif type(payload) == discord_components.message.ComponentMessage:
                            payload.content = payload.content.strip()
                            if param == "Name":
                                if " " not in payload.content:
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
                            await get_reg_info(["```diff\n- ", f"\n+ {payload.content}\n```"])
                            await message.edit(embed=edit_embed, components=[[but_save, but_cancel]])

                            # Get Button Response
                            try:
                                but_res = await self.client.wait_for(
                                    "button_click", check=lambda b: b.author == ctx.author, timeout=60)
                            except asyncio.exceptions.TimeoutError:
                                await timeout()
                                return True
                            else:
                                # Saves the response to file
                                if but_res.component.label == "Save":
                                    self.users[user][param] = payload.content
                                    edit_embed.set_footer(text=f"Changes made to {param} saved successfully.")
                                    cancel_save = False
                                # Does nothing, loops the editing for the same profile parameter
                                elif but_res.component.label == "Cancel":
                                    edit_embed.set_footer(text="")
                                await but_res.respond(type=InteractionType.UpdateMessage, embed=edit_embed)

        await get_reg_info(["", ""])
        await message.edit(embed=edit_embed, components=[])
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

        if "Volunteer" not in str(ctx.guild.roles):
            await ctx.guild.create_role(name="Volunteer", permissions=ctx.guild.default_role.permissions, hoist=False,
                                        reason="Guild Role Not Found")

    async def disp_branch(self, ctx, branch, group, leader):
        if group:
            await self.disp_group(ctx, branch, group, leader)
        else:
            num_groups = 0
            group_list = ""
            for group in self.roles_list[branch]:
                group_list += f"> {group}  {self.roles_list[branch][group]['Logo']}\n"
                num_groups += 1
            groups_embed = discord.Embed(title=f"List of {branch}s", description=group_list, colour=0X2072AA)
            groups_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            groups_embed.set_footer(text=f"For more information, use -{branch} <{branch} type>")
            if num_groups == 1:
                await self.disp_group(ctx, branch, branch, leader)
            else:
                await ctx.send(embed=groups_embed)

    async def disp_group(self, ctx, branch, group, leader):
        async def get_members():
            member_list = ""
            for member in ctx.guild.members:
                if group_role in member.roles:
                    member_list += f"{member.mention} "
            if member_list == "":
                member_list = "None"
            group_embed.set_field_at(index=2, name="MEMBERS:", value=member_list, inline=False)

        # Filter Group
        match = False
        for g in self.roles_list[branch]:
            if group.lower() in g.lower():
                group, match = g, True
                break
        # End command if no filtered result
        if not match:
            return await ctx.reply(f"\"{group}\" is not a \"{branch}\"")
        elif leader:
            match = False
            # Filter leaders
            for l in self.roles_list[branch][group]["Leaders"]:
                if leader.lower() in l.lower():
                    leader, match = l, True
                    break
            if not match:
                return await ctx.reply(f"\"{leader}\" is not a recognisable option in \"{group}\"")
            else:
                return await self.disp_leader(ctx, branch, group, leader)

        # Button Init
        but_join = Button(style=ButtonStyle.green, label="Join", emoji="🖋️")
        but_resign = Button(style=ButtonStyle.red, label="Resign", emoji="🛑")
        but_cancel = Button(style=ButtonStyle.grey, label="Cancel", emoji="❌")

        try:
            # Group Info
            group_embed = discord.Embed(title=group, colour=0X2072AA)
            group_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            group_embed.set_thumbnail(url=self.roles_list[branch][group]["Thumbnail"])
            leader_list = ""
            for leader in self.roles_list[branch][group]["Leaders"]:
                leader_list += f"**{leader}:** {' '.join([id.join(['<@', '>']) for id in self.roles_list[branch][group]['Leaders'][leader]['DiscordID'].split(', ')])}\n"

            if leader_list == "":
                leader_list = "None"
            group_embed.add_field(name="LEADERS:", value=leader_list)
            group_embed.add_field(name="DESCRIPTION:", value=self.roles_list[branch][group]["Description"], inline=False)
            group_embed.add_field(name="MEMBERS", value="None", inline=False)
            group_role = discord.utils.get(ctx.guild.roles, name=group)
            await get_members()
            message = await ctx.send(embed=group_embed, components=[[but_join, but_resign, but_cancel]])

            # Join/Resign
            try:
                but_choice = await self.client.wait_for("button_click", check=lambda b: b.author == ctx.author, timeout=60)
                if but_choice.component.label == "Join":
                    if str(ctx.author.id) not in self.users:
                        group_embed.set_footer(text="ERROR: Registration not found! Please register with -register")
                    elif self.roles_list[branch][group]["Private"] == "True":
                        group_embed.set_footer(text="You cannot join a private branch/group")
                    elif group_role not in ctx.author.roles:
                        await ctx.author.add_roles(group_role)
                        group_embed.set_footer(text=f"You have joined {group_role}")
                        await get_members()
                    else:
                        group_embed.set_footer(text=f"You are already in {group_role}")
                    if len(ctx.author.roles) >= 1:
                        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name="Volunteer"))
                elif but_choice.component.label == "Resign":
                    if self.roles_list[branch][group]["Private"] == "True":
                        group_embed.set_footer(text=f"Please contact {ctx.guild.owner.mention} to resign from {branch}")
                    elif group_role in ctx.author.roles:
                        await ctx.author.remove_roles(group_role)
                        group_embed.set_footer(text=f"You have resigned from {group_role}")
                        await get_members()
                    else:
                        group_embed.set_footer(text=f"You were never a part of {group_role}")
                    if len(ctx.author.roles) <= 1:
                        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Volunteer"))
                elif but_choice.component.label == "Cancel":
                    group_embed.set_footer(text="COMMAND TERMINATED")
                await but_choice.respond(type=InteractionType.UpdateMessage, embed=group_embed, components=[])
            except asyncio.TimeoutError:
                group_embed.set_footer(text="No response received. COMMAND TERMINATED.")
            await message.edit(embed=group_embed, components=[])

        except KeyError:
            await ctx.reply(f"The specific {branch} you were looking for cannot be resolved")

    async def disp_leader(self, ctx, branch, group, leader):
        leader_list_raw = self.roles_list[branch][group]["Leaders"][leader]["DiscordID"].split(", ")
        leader_list = f"**{leader}:** {' '.join([id.join(['<@', '>']) for id in leader_list_raw])}\n"
        if len(leader_list_raw) > 1:
            url = self.roles_list[branch][group]["Thumbnail"]
        else:
            user = await self.client.fetch_user(int(leader_list_raw[0]))
            url = user.avatar_url
        lead_embed = discord.Embed(title=f"{group} {leader}", description=f"{leader_list}\n\n**DESCRIPTION:**\n{self.roles_list[branch][group]['Leaders'][leader]['Description']}", colour=0X2072AA)
        lead_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        lead_embed.set_thumbnail(url=url)
        await ctx.send(embed=lead_embed)

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

            if len(ctx.author.roles) <= 1:
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Volunteer"))
            await ctx.reply("You have successfully registered!")
            await ctx.author.send("Welcome to IEEE McMaster Student Branch! Please read our official rules below:")
            await asyncio.sleep(3)
            await self.rules(ctx)
            await asyncio.sleep(30)
            await ctx.author.send("Your current role in our club is ***'Volunteer'***. As you join committees or "
                                  "chapters, this role will change.")

    @commands.command(hidden=True)
    async def kill(self, ctx, victim: discord.User = None):
        if victim and ctx.author != victim:
            await ctx.send(f"{ctx.author.mention} killed {victim.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} killed themself")

    @commands.command(description="Shows the upper echelon that runs and maintains IEEE Student Branch")
    async def mainbranch(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Main Branch", group, leader)

    @commands.command(description="Shows all joinable Chapters and their descriptions.",
                      aliases=["chapters", "chap", "chaps"])
    async def chapter(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Chapter", group, leader)

    @commands.command(description="Shows all joinable Committees and their descriptions.",
                      aliases=["committees", "comm", "comms"])
    async def committee(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Committee", group, leader)


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
