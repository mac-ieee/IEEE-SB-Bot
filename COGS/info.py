import discord
import json
from discord.ext import commands
import os
import asyncio


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def set_name(self, users, user):
        await self.client.send(f"{user.mention}, please enter your **first** and **last name**")
        name_response = await self.client.wait_for(
            "message", check=lambda message: message.author == user, timeout=15)
        name_response = name_response.content.strip().split(" ")
        if not (name_response[0] + name_response[1]).isalpha():
            raise InvalidNameError
        users[user.id] = {}
        users[user.id]["First Name"] = name_response[0]
        users[user.id]["Last Name"] = name_response[1]


    @commands.command()
    async def rules(self, ctx):
        rules = open(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot\Information\rules.txt", "r")
        await ctx.author.send(rules.read())

    @commands.command()
    async def register(self, ctx):
        os.chdir(r"C:\Users\Evan\Documents\GitHub\IEEE-SB-Bot")
        with open("users.json", "r") as file:
            users = json.load(file)

        if f"{ctx.author.id}" in users:
            await ctx.send(f"{ctx.author.mention} You are already registered")
        else:
            try:
                # Get Email
                await ctx.send(f"{ctx.author.mention}, please enter your **McMaster email address**")
                email_response = await self.client.wait_for(
                    "message", check=lambda message: message.author == ctx.author, timeout=15)
                email_response = email_response.content.strip()
                if not email_response.endswith("mcmaster.ca"):
                    raise InvalidEmailError
                users[ctx.author.id]["MAC Email"] = email_response
                # Get Email
                await ctx.send(f"{ctx.author.mention},"
                               f" please enter your **program name**")
                program_response = await self.client.wait_for(
                    "message", check=lambda message: message.author == ctx.author, timeout=15)
                program_response = program_response.content.strip()
                users[ctx.author.id]["Program"] = program_response
                if not program_response[0].isalpha():
                    raise InvalidProgramError
                # Get Year
                await ctx.send(f"{ctx.author.mention}, What **year** are you in?")
                year_response = await self.client.wait_for(
                    "message", check=lambda message: message.author == ctx.author, timeout=15)
                year_response = int(year_response.content.strip())
                users[ctx.author.id]["Year"] = year_response

            except asyncio.TimeoutError:
                return await ctx.send(f"Sorry {ctx.author.mention}, you took to long to respond. Command Terminated.")
            except InvalidNameError:
                return await ctx.send(
                    f"Sorry {ctx.author.mention}, names can only consist of letters. Please try again")
            except IndexError:
                return await ctx.send(f"Sorry {ctx.author.mention}, we need your last name as well. Please try again")
            except InvalidEmailError:
                return await ctx.send(f"Sorry {ctx.author.mention}, we can't use that email address. Please try again")
            except InvalidProgramError:
                return await ctx.send(
                    f"Sorry {ctx.author.mention}, invalid character in program name. Please try again")
            except ValueError:
                return await ctx.send(f"Sorry {ctx.author.mention}, we were expecting a number. Please try again")

            users[ctx.author.id]["Roles"] = None
            users[ctx.author.id]["Level"] = 1
            users[ctx.author.id]["Experience"] = 0
            users[ctx.author.id]["Coins"] = 500
            with open("users.json", "w") as file:
                json.dump(users, file)
            await ctx.send(
                f"{ctx.author.mention} has successfully registered as \"{name_response[0]} {name_response[1]}\"")
            # Avoid error: Bot cannot override server owner's permissions,
            if ctx.author.id != ctx.guild.owner_id:
                await ctx.author.edit(nick=name_response[0])
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
