import discord
import json
from discord.ext import commands
import os
import asyncio


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

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
            users[ctx.author.id] = {}
            users[ctx.author.id]["Roles"] = None
            await ctx.send(f"{ctx.author.mention}, please enter your first and last name")
            # Get name
            try:
                name_response = await self.client.wait_for(
                    "message", check=lambda message: message.author == ctx.author, timeout=15)
                given_names = name_response.content.strip().split(" ")
                if not (given_names[0]+given_names[1]).isalpha():
                    raise InvalidNameError
                users[ctx.author.id] = {}
                users[ctx.author.id]["First Name"] = given_names[0]
                users[ctx.author.id]["Last Name"] = given_names[1]
                users[ctx.author.id]["Roles"] = None
                users[ctx.author.id]["Level"] = 1
                users[ctx.author.id]["Experience"] = 0
                users[ctx.author.id]["Coins"] = 500
                await ctx.send(
                    f"{ctx.author.mention} has successfully registered as \"{given_names[0]} {given_names[1]}\"")
                with open("users.json", "w") as file:
                    json.dump(users, file)
                # Avoid error: Bot cannot override server owner's permissions,
                if ctx.author.id != ctx.guild.owner_id:
                    await ctx.author.edit(nick=given_names[0])
                else:
                    await ctx.send(
                        f"Server owners must change their own nickname")
            except asyncio.TimeoutError:
                return await ctx.send(f"Sorry {ctx.author.mention}, you took to long to respond. Please try again")
            except InvalidNameError:
                return await ctx.send(
                    f"Sorry {ctx.author.mention}, names can only consist of letters. Please try again")
            except IndexError:
                return await ctx.send(f"Sorry {ctx.author.mention}, we need your last name as well. Please try again")

    @commands.command()
    async def committees(self, ctx, sumfuc):
        pass

def setup(client):
    client.add_cog(Info(client))


class InvalidNameError(Exception):
    pass
