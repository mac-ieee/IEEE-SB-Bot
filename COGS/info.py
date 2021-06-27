import discord
from discord.ext import commands
import os
import json
import asyncio


class Info(commands.Cog):
    roles_list = {}
    role_groups = []

    def __init__(self, client):
        self.client = client
        with open(r"Information/roles_list.json", "r") as file:
            self.roles_list = json.load(file)

        for role in self.roles_list:
            if self.roles_list[role]["Group"] != "" and not self.role_groups.__contains__((self.roles_list[role]["Group"] + "s").lower()):
                self.role_groups.append((self.roles_list[role]["Group"] + "s").lower())
        self.role_group.update(aliases=self.role_groups)

    async def set_name(self, ctx, users, user):
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
            return await self.set_name(ctx, users, user)
        except IndexError:
            await ctx.send(f"Sorry {user.mention}, we need your last name as well. Please try again")
            return await self.set_name(ctx, users, user)

    async def set_email(self, ctx, users, user):
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
            return await self.set_email(ctx, users, user)

    async def set_program(self, ctx, users, user):
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
            return await self.set_program(ctx, users, user)

    async def set_year(self, ctx, users, user):
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
            return await self.set_year(ctx, users, user)

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

        for role in self.roles_list:
            if role not in str(ctx.guild.roles):
                await ctx.guild.create_role(
                    name=role, permissions=ctx.guild.default_role.permissions, hoist=True, reason="Guild Role Not Found"
                )
        for role in self.roles_list:
            if self.roles_list[role]["Group"] != "" and not self.role_groups.__contains__(
                    (self.roles_list[role]["Group"] + "s").lower()):
                self.role_groups.append((self.roles_list[role]["Group"] + "s").lower())
        Info.role_group.update(aliases=self.role_groups)

    async def disp_roles(self, ctx, group, role):
        if role:
            # Filter Group
            roles_str = str(self.roles_list)
            role_lower = role.lower() + " " + group[0:-1]
            role_index = roles_str.lower().find(role_lower)
            if role_lower in roles_str.lower():
                role = roles_str[role_index:role_index+len(role_lower)]
            else:
                role = role.title() + " " + group[0:-1].title()

            # Role Info
            roles_embed = discord.Embed(title=role, colour=0X2072AA)
            if role in self.roles_list and self.roles_list[role]["Group"].lower() in group.lower():
                roles_embed.set_thumbnail(url=self.roles_list[role]["Thumbnail"])
                leader_list = ""
                for leader in self.roles_list[role]["Leaders"]:
                    leader_list += \
                        f"**{leader}:** <@{self.roles_list[role]['Leaders'][leader]}>\n"
                if leader_list == "":
                    leader_list = "None"
                roles_embed.add_field(name="LEADERS:", value=leader_list)
                roles_embed.add_field(name="DESCRIPTION:", value=self.roles_list[role]["Description"], inline=False)
                member_list = ""
                for member in ctx.guild.members:
                    if discord.utils.get(ctx.guild.roles, name=role) in member.roles:
                        member_list += f"{member.mention} "
                if member_list == "":
                    member_list = "None"
                roles_embed.add_field(name="MEMBERS:", value=member_list, inline=False)
                roles_embed.set_footer(text=f"To join/leave {role}, type 'join' or 'leave'")
                roles_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=roles_embed)
            else:
                await ctx.reply(f"There is no {role}")
            role = discord.utils.get(ctx.guild.roles, name=role)

            # Join/Leave
            response = await self.client.wait_for("message", check=lambda message: message.author == ctx.author)
            if response.content == "join":
                if role not in ctx.author.roles:
                    await response.reply(f"You have joined {role}")
                    await ctx.author.add_roles(role)
                else:
                    await response.reply(f"You are already in {role}")
            elif response.content == "leave":
                if role in ctx.author.roles:
                    await response.reply(f"You have resigned from {role}")
                    await ctx.author.remove_roles(role)
                else:
                    await response.reply(f"You were never a part of {role}")


        # Display All Roles
        else:
            roles_embed = discord.Embed(title=group.title(), colour=0X2072AA)
            for role in self.roles_list:
                if self.roles_list[role]["Group"].lower() in group.lower():
                    roles_embed.add_field(
                        name=f"{role}  {self.roles_list[role]['Logo']}",
                        value=self.roles_list[role]["Description"], inline=False
                    )
            roles_embed.set_footer(text=f"For more information, use -{group} <{group[0:-1]}>")
            roles_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=roles_embed)


    @commands.command()
    async def rules(self, ctx):
        rules = open(r"Information/rules.txt", "r")
        await ctx.author.send(rules.read())

    @commands.command()
    async def register(self, ctx):
        with open("users.json", "r") as file:
            users = json.load(file)

        if str(ctx.author.id) in users:
            await ctx.send(f"{ctx.author.mention} You are already registered")
        else:
            users[ctx.author.id] = {}
            try:
                names = await self.set_name(ctx, users, ctx.author)
                users[ctx.author.id]["First Name"] = names[0]
                users[ctx.author.id]["Last Name"] = names[1]
                users[ctx.author.id]["Email"] = await self.set_email(ctx, users, ctx.author)
                users[ctx.author.id]["Program"] = await self.set_program(ctx, users, ctx.author)
                users[ctx.author.id]["Year"] = await self.set_year(ctx, users, ctx.author)
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

    @commands.command()
    async def kill(self, ctx, victim: discord.User = None):
        if victim and ctx.author != victim:
            await ctx.send(f"{ctx.author.mention} killed {victim.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} killed themself")

    @commands.command()
    async def role_group(self, ctx, *, role=None):
        await self.sync_roles(ctx)
        await self.disp_roles(ctx, ctx.invoked_with, role)


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


