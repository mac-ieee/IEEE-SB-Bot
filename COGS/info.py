import enum
import os
import discord
from discord.ext import commands
import json
from discord import ButtonStyle, TextStyle, app_commands
from discord.ui import Button, TextInput


class ProfileModal(discord.ui.Modal, title="Edit Profile"):
    def __init__(self, guild, ctx, cmd):
        super().__init__()
        self.guild = guild
        self.ctx = ctx
        self.cmd = cmd
        with open("users.json", "r") as file:
            self.users = json.load(file)

    name = TextInput(label="Enter your Name", placeholder="eg. Hououin Kyouma",
                     required=True, max_length=64, style=TextStyle.short)
    dmail = TextInput(label="Enter your MAC Email", placeholder="eg. kyoumah@mcmaster.ca",
                      required=True, max_length=64, style=TextStyle.short)
    program = TextInput(label="Enter your Program", placeholder="eg. Engineering",
                        required=True, max_length=32, style=TextStyle.short)
    year = TextInput(label="Enter your Year / Level", placeholder="eg. 5.1",
                     required=True, max_length=3, style=TextStyle.short)
    about = TextInput(label="Tell us about yourself (Optional)", placeholder="eg. I AM MAD SCIENTIST! IT SO COOL!",
                      required=False, max_length=128, style=TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        self.users[self.ctx.user.id] = {
            "Name": self.name.value,
            "Email": self.dmail.value,
            "Program": self.program.value,
            "Year": self.year.value,
            "About": self.about.value,
            "Title": "Official IEEE Member",
            "Offences": 0,
            "Level": 1,
            "Experience": 0,
            "Coins": 500
        }
        with open("users.json", "w") as file:
            json.dump(self.users, file, indent=4)
        if self.cmd.name.strip() == "register":
            if not isinstance(interaction.channel, discord.channel.DMChannel):
                await interaction.response.send_message("Please check your DMs for additional steps", ephemeral=True)
            else:
                await interaction.response.defer()

            # Button
            but_agree = Button(style=ButtonStyle.grey, label="I have read and agree to all the rules", emoji="✔")

            async def agree_callback(interaction):
                but_agree.disabled = True
                but_agree.style = ButtonStyle.green

                member = self.guild.get_member(interaction.user.id)
                if len(member.roles) <= 1:
                    await member.add_roles(discord.utils.get(self.guild.roles, name="Volunteer"))
                await interaction.response.edit_message(content=msg.content, view=view)
                await interaction.user.send("You have successfully registered! "
                                            "You now have access to the **get-roles** channel")

            but_agree.callback = agree_callback
            view = discord.ui.View(timeout=None)
            view.add_item(but_agree)
            rules = open(r"Information/rules.txt", "r")
            msg = await interaction.user.send(f"**Welcome to IEEE McMaster Student Branch!**\nBefore you can access "
                                                f"the full server, please read and agree to the server rules:\n\n"
                                                f"{rules.read()}", view=view)

    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(error, ephemeral=True)


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
                print(f"Warning: {branch} from roles_list has not been declared as a command")

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
                group_list += f"> {self.roles_list[branch][group]['Logo']}  {group}\n"
                num_groups += 1
            groups_embed = discord.Embed(title=f"List of {branch}s", description=group_list, colour=0X2072AA)
            groups_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            groups_embed.set_footer(text=f"For more information, use -{branch} <{branch} type>")
            if num_groups == 1:
                await self.disp_group(ctx, branch, branch, leader)
            else:
                await ctx.send(embed=groups_embed)

    async def disp_group(self, ctx, branch, group, leader):
        pass

    async def disp_leader(self, ctx, branch, group, leader):
        leader_list_raw = self.roles_list[branch][group]["Leaders"][leader]["DiscordID"].split(", ")
        leader_list = f"**{leader}:** {' '.join([id.join(['<@', '>']) for id in leader_list_raw])}\n"
        if len(leader_list_raw) > 1:
            url = self.roles_list[branch][group]["Thumbnail"]
        else:
            user = await self.client.fetch_user(int(leader_list_raw[0]))
            url = user.avatar.url
        lead_embed = discord.Embed(
            title=f"{group} {leader}",
            description=f"{leader_list}\n\n**DESCRIPTION:**\n"
                        f"{self.roles_list[branch][group]['Leaders'][leader]['Description']}",
            colour=0X2072AA)
        lead_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        lead_embed.set_thumbnail(url=url)
        await ctx.send(embed=lead_embed)

    @app_commands.command(name="rules", description="PMs you the server's official rules")
    async def rules(self, ctx):
        rules = open(r"Information/rules.txt", "r")
        await ctx.response.send_message(rules.read(), ephemeral=True)

    @app_commands.command(name="register", description="Officially registers you as an IEEE Student Branch member")
    async def register(self, ctx):
        with open("users.json", "r") as file:
            self.users = json.load(file)

        guild = self.client.get_guild(int(os.getenv("GUILD_ID")))
        if str(ctx.user.id) in self.users:
            await ctx.response.send_message("You are already registered.", ephemeral=True)
        else:
            modal = ProfileModal(guild, ctx, ctx.command)
            modal.title = "Create Profile"
            await ctx.response.send_modal(modal)

    @commands.command(name="mainbranch",
                      description="Shows the upper echelon that runs and maintains IEEE Student Branch")
    async def mainbranch(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Main Branch", group, leader)

    @commands.command(name="chapters", description="Shows all joinable Chapters and their descriptions.")
    async def chapter(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Chapter", group, leader)

    @commands.command(name="committee", description="Shows all joinable Committees and their descriptions.")
    async def committee(self, ctx, group=None, *, leader=None):
        await self.sync_roles(ctx)
        await self.disp_branch(ctx, "Committee", group, leader)


async def setup(client):
    await client.add_cog(Info(client))


class InvalidNameError(Exception):
    pass


class InvalidEmailError(Exception):
    pass


class InvalidProgramError(Exception):
    pass


class ForcedInteruptError(Exception):
    pass
