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
            if user.id != ctx.guild.owner_id:
                await user.edit(nick=name_response[0])
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
            if "stop" in email_response or "cancel" in email_response or "quit" in email_response:
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
            if "stop" in program_response or "cancel" in program_response or "quit" in program_response:
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
            if "stop" in year_response or "cancel" in year_response or "quit" in year_response:
                raise ForcedInteruptError
            return int(year_response)
        except ValueError:
            await ctx.send(f"Sorry {user.mention}, we were expecting a number. Please try again")
            return await self.set_year(ctx, users, user)

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

    @commands.command()
    async def kill(self, ctx, victim: discord.User = None):
        if victim:
            await ctx.send(f"{ctx.author.mention} killed {victim.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} killed themself")

    @commands.command()
    async def test(self, ctx):
        print(ctx.author.nick)

    @commands.command(aliases=["chaps"])
    async def chapters(self, ctx, chaps=None):
        role = False
        # Chapters
        if chaps == "computer":
            chaps_embed = discord.Embed(title="Computer Chapter", colour=0X2072AA)
            chaps_embed.add_field(name="Description:", value=f"<text>", inline=False)
            chaps_embed.add_field(name="Members:", value=f"<text>", inline=False)
            chaps_embed.set_footer(text="To join Computer Chapter, type join")
            role = discord.utils.get(ctx.guild.roles, name="Computer Chapter")
        elif chaps == "embs":
            chaps_embed = discord.Embed(title="EMBS Chapter", colour=0X2072AA)
            chaps_embed.add_field(name="Description:", value=f"<text>", inline=False)
            chaps_embed.add_field(name="Members:", value=f"<text>", inline=False)
            chaps_embed.set_footer(text="To join EMBS Chapter, type join")
            role = discord.utils.get(ctx.guild.roles, name="EMBS Chapter")
        elif chaps == "pes":
            chaps_embed = discord.Embed(title="PES Chapter", colour=0X2072AA)
            chaps_embed.add_field(name="Description:", value=f"<text>", inline=False)
            chaps_embed.add_field(name="Members:", value=f"<text>", inline=False)
            chaps_embed.set_footer(text="To join PES Chapter, type join")
            role = discord.utils.get(ctx.guild.roles, name="PES Chapter")
        else:
            chaps_embed = discord.Embed(title="Chapters", colour=0X2072AA)
            chaps_embed.add_field(name="Computer Chapter", value=f"**Desc.:** <text>", inline=False)
            chaps_embed.add_field(name="EMBS Chapter", value=f"**Desc.:** <text>", inline=False)
            chaps_embed.add_field(name="PES Chapter", value=f"**Desc.:** <text>", inline=False)
        chaps_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=chaps_embed)
        # Join Response
        response = await self.client.wait_for("message", check=lambda message: message.author == ctx.author)
        if response.content == "join" and role:
            await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
            await ctx.author.add_roles(role)

    @commands.command(aliases=["comms"])
    async def committees(self, ctx, comms=None):
        role = False
        # Committees
        if comms == "discord":
            comms_embed = discord.Embed(title="Discord Committee", colour=0X2072AA)
            comms_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/776205209046482995.png?v=1")
            comms_embed.add_field(name="Description:", value=f"<text>", inline=False)
            comms_embed.add_field(name="Members:", value=f"<text>", inline=False)
            comms_embed.set_footer(text="To join Discord Committee, type join")
            role = discord.utils.get(ctx.guild.roles, name="Discord Committee")
        elif comms == "social":
            comms_embed = discord.Embed(title="Social Committee", colour=0X2072AA)
            comms_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/776205198371979325.png?v=1")
            comms_embed.add_field(name="Description:", value=f"<text>", inline=False)
            comms_embed.add_field(name="Members:", value=f"<text>", inline=False)
            comms_embed.set_footer(text="To join Social Committee, type join")
            role = discord.utils.get(ctx.guild.roles, name="Social Committee")
        elif comms == "website":
            comms_embed = discord.Embed(title="Website Committee", colour=0X2072AA)
            comms_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/776205187349086290.png?v=1")
            comms_embed.add_field(name="Description:", value=f"<text>", inline=False)
            comms_embed.add_field(name="Members:", value=f"<text>", inline=False)
            comms_embed.set_footer(text="To join Website Committee, type join")
            role = discord.utils.get(ctx.guild.roles, name="Website Committee")
        elif comms == "workshop":
            comms_embed = discord.Embed(title="Workshop Committee", colour=0X2072AA)
            comms_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/776205171130368061.png?v=1")
            comms_embed.add_field(name="Description:", value=f"<text>", inline=False)
            comms_embed.add_field(name="Members:", value=f"<text>", inline=False)
            comms_embed.set_footer(text="To join Workshop Committee, type join")
            role = discord.utils.get(ctx.guild.roles, name="Workshop Committee")
        else:
            comms_embed = discord.Embed(title="Committees", description="To join a committee, react with the appropriate emoji", colour=0X2072AA)
            comms_embed.add_field(name="Discord Committee  <:discord:776205209046482995>", value=f"**Desc.:** <text>", inline=False)
            comms_embed.add_field(name="Social Committee  <:social:776205198371979325>", value=f"**Desc.:** <text>", inline=False)
            comms_embed.add_field(name="Website Committee  <:website:776205187349086290>", value=f"**Desc.:** <text>", inline=False)
            comms_embed.add_field(name="Workshop Committee  <:workshop:776205171130368061>", value=f"**Desc.:** <text>", inline=False)
            comms_embed.set_footer(text="To get committee members list, use -committees <commitee>")
        comms_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        msg = await ctx.send(embed=comms_embed)

        # Response
        if role:
            response = await self.client.wait_for("message", check=lambda message: message.author == ctx.author)
            if response.content == "join":
                await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
                await ctx.author.add_roles(role)
        else:
            await msg.add_reaction(emoji="discord:776205209046482995")
            await msg.add_reaction(emoji="social:776205198371979325")
            await msg.add_reaction(emoji="website:776205187349086290")
            await msg.add_reaction(emoji="workshop:776205171130368061")
            def check(reaction, user):
                return user == ctx.author
            reaction = await self.client.wait_for("reaction_add", check=check)
            if "776205209046482995" in str(reaction):
                role = discord.utils.get(ctx.guild.roles, name="Discord Committee")
                await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
                await ctx.author.add_roles(role)
            elif "776205198371979325" in str(reaction):
                role = discord.utils.get(ctx.guild.roles, name="Social Committee")
                await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
                await ctx.author.add_roles(role)
            elif "776205187349086290" in str(reaction):
                role = discord.utils.get(ctx.guild.roles, name="Website Committee")
                await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
                await ctx.author.add_roles(role)
            elif "776205171130368061" in str(reaction):
                role = discord.utils.get(ctx.guild.roles, name="Workshop Committee")
                await ctx.send(f"{ctx.author.mention} has joined {role.mention}")
                await ctx.author.add_roles(role)

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
