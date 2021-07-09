import discord
from discord.ext import commands
import os
import json
import asyncio


class Info(commands.Cog, description="Info :scroll:"):
    roles_list = {}
    new_cmds = {}

    def __init__(self, client):
        self.client = client
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


    async def set_name(self, ctx, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **first** and **last name**")
            name_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            if name_response.content == "stop" or name_response.content == "cancel" or name_response.content == "quit":
                raise ForcedInteruptError
            name_response = name_response.content.strip().split(" ")
            if not (name_response[0] + name_response[1]).isalpha():
                raise InvalidNameError
            return name_response
        except InvalidNameError:
            await ctx.send(
                f"Sorry {user.mention}, names can only consist of letters. Please try again")
            return await self.set_name(ctx, user)
        except IndexError:
            await ctx.send(f"Sorry {user.mention}, we need your last name as well. Please try again")
            return await self.set_name(ctx, user)

    async def set_email(self, ctx, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **McMaster email address**")
            email_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            email_response = email_response.content.strip()
            if email_response == "stop" or email_response == "cancel" or email_response == "quit":
                raise ForcedInteruptError
            if not email_response.endswith("mcmaster.ca"):
                raise InvalidEmailError
            return email_response
        except InvalidEmailError:
            await ctx.send(f"Sorry {user.mention}, we can't use that email address. Please try again")
            return await self.set_email(ctx, user)

    async def set_program(self, ctx, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **program name**")
            program_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            program_response = program_response.content.strip()
            if program_response == "stop" or program_response == "cancel" or program_response == "quit":
                raise ForcedInteruptError
            if not program_response.replace(" ", "I").isalpha():
                raise InvalidProgramError
            return program_response
        except InvalidProgramError:
            await ctx.send(
                f"Sorry {user.mention}, program names can only use letter. Please try again")
            return await self.set_program(ctx, user)

    async def set_year(self, ctx, user):
        try:
            await ctx.send(f"{user.mention}, What **year** are you in?")
            year_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            year_response = year_response.content.strip()
            if year_response == "stop" or year_response == "cancel" or year_response == "quit":
                raise ForcedInteruptError
            return int(year_response)
        except ValueError:
            await ctx.send(f"Sorry {user.mention}, we were expecting a number. Please try again")
            return await self.set_year(ctx, user)

    async def set_desc(self, ctx, user):
        await ctx.send(f"{user.mention}, please enter your desired **description**")
        desc_response = await self.client.wait_for("message", check=lambda message: message.author == user, timeout=60)
        desc_response = desc_response.content.strip()
        if desc_response == "stop" or desc_response == "cancel" or desc_response == "quit":
            raise ForcedInteruptError
        return desc_response

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
            users = json.load(file)

        if str(ctx.author.id) in users:
            await ctx.send(f"{ctx.author.mention} You are already registered")
        else:
            users[ctx.author.id] = {}
            try:
                names = await self.set_name(ctx, ctx.author)
                users[ctx.author.id]["First Name"] = names[0]
                users[ctx.author.id]["Last Name"] = names[1]
                users[ctx.author.id]["Email"] = await self.set_email(ctx, ctx.author)
                users[ctx.author.id]["Program"] = await self.set_program(ctx, ctx.author)
                users[ctx.author.id]["Year"] = await self.set_year(ctx, ctx.author)
                users[ctx.author.id]["Description"] = "No description. To add one, type -p edit description"
                await ctx.author.edit(nick=names[0])
            except asyncio.TimeoutError:
                return await ctx.send(f"Sorry {ctx.author.mention}, you took to long to respond. Command Terminated.")
            except ForcedInteruptError:
                return await ctx.send(f"{ctx.author.mention} terminated the command")
            except discord.Forbidden:
                await ctx.send("**ERROR:** Cannot change discord nickname! Permissions missing or too low!")

            users[ctx.author.id]["Title"] = "Official IEEE Member"
            users[ctx.author.id]["Offences"] = 0
            users[ctx.author.id]["Level"] = 1
            users[ctx.author.id]["Experience"] = 0
            users[ctx.author.id]["Coins"] = 500
            with open("users.json", "w") as file:
                json.dump(users, file, indent=4)
            await ctx.send(
                f"{ctx.author.mention} has successfully registered")

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


