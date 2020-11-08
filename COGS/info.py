import discord
from discord.ext import commands
import os
import json
import asyncio


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def set_name(self, ctx, users, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **first** and **last name**")
            name_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            if "stop" in name_response.content or "cancel" in name_response.content or "quit" in name_response.content:
                raise ForcedInteruptError
            name_response = name_response.content.strip().split(" ")
            if not (name_response[0] + name_response[1]).isalpha():
                raise InvalidNameError
            return name_response
        except InvalidNameError:
            await ctx.send(
                f"Sorry {user.mention}, names can only consist of letters. Please try again")
            await self.set_name(ctx, users, user)
        except IndexError:
            await ctx.send(f"Sorry {user.mention}, we need your last name as well. Please try again")
            await self.set_name(ctx, users, user)

    async def set_email(self, ctx, users, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **McMaster email address**")
            email_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            email_response = email_response.content.strip()
            if "stop" in email_response or "cancel" in email_response or "quit" in email_response:
                raise ForcedInteruptError
            if not email_response.endswith("mcmaster.ca"):
                raise InvalidEmailError
            return email_response
        except InvalidEmailError:
            await ctx.send(f"Sorry {user.mention}, we can't use that email address. Please try again")
            await self.set_email(ctx, users, user)

    async def set_program(self, ctx, users, user):
        try:
            await ctx.send(f"{user.mention}, please enter your **program name**")
            program_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            program_response = program_response.content.strip()
            if "stop" in program_response or "cancel" in program_response or "quit" in program_response:
                raise ForcedInteruptError
            if not program_response.replace(" ", "I").isalpha():
                raise InvalidProgramError
            return program_response
        except InvalidProgramError:
            await ctx.send(
                f"Sorry {user.mention}, program names can only use letter. Please try again")
            await self.set_program(ctx, users, user)

    async def set_year(self, ctx, users, user):
        try:
            await ctx.send(f"{user.mention}, What **year** are you in?")
            year_response = await self.client.wait_for(
                "message", check=lambda message: message.author == user, timeout=60)
            year_response = year_response.content.strip()
            if "stop" in year_response or "cancel" in year_response or "quit" in year_response:
                raise ForcedInteruptError
            return int(year_response)
        except ValueError:
            await ctx.send(f"Sorry {user.mention}, we were expecting a number. Please try again")
            await self.set_year(ctx, users, user)

    @commands.command()
    async def rules(self, ctx):
        rules = open(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot\Information\rules.txt", "r")
        await ctx.author.send(rules.read())

    @commands.command()
    async def register(self, ctx):
        os.chdir(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot")
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
            except asyncio.TimeoutError:
                return await ctx.send(f"Sorry {ctx.author.mention}, you took to long to respond. Command Terminated.")
            except ForcedInteruptError:
                return await ctx.send(f"{ctx.author.mention} terminated the command")

            users[ctx.author.id]["Title"] = "Official IEEE Member"
            users[ctx.author.id]["Committees"] = "None"
            users[ctx.author.id]["Level"] = 1
            users[ctx.author.id]["Experience"] = 0
            users[ctx.author.id]["Coins"] = 500
            with open("users.json", "w") as file:
                json.dump(users, file)
            await ctx.send(
                f"{ctx.author.mention} has successfully registered")
            # Avoid error: Bot cannot override server owner's permissions,
            if ctx.author.id != ctx.guild.owner_id:
                await ctx.author.edit(nick=users[ctx.author.id]["First Name"])
            else:
                await ctx.send(
                    f"Server owners must change their own nickname")
                
    @commands.command()
    async def committees(self, ctx, sumfuk):
        pass


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
