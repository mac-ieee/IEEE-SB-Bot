import discord
from discord.ext import commands
from discord import ButtonStyle, TextStyle, app_commands
from discord.ui import Button, TextInput
import json


class ProfileModal(discord.ui.Modal, title="Edit Profile"):
    def __init__(self, ctx, cmd):
        super().__init__()
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
        self.users[str(self.ctx.user.id)]["Name"] = self.name.value
        self.users[str(self.ctx.user.id)]["Email"] = self.dmail.value
        self.users[str(self.ctx.user.id)]["Program"] = self.program.value
        self.users[str(self.ctx.user.id)]["Year"] = self.year.value
        self.users[str(self.ctx.user.id)]["About"] = self.about.value

        with open("users.json", "w") as file:
            json.dump(self.users, file, indent=4)
        
        if self.cmd.name.strip() == "edit":
            if not isinstance(interaction.channel, discord.channel.DMChannel):
                await interaction.response.send_message("You profile has been edited successfully!", ephemeral=True)


    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}", ephemeral=True)


class Test(commands.Cog, description="Test :tools:"):
    def __init__(self, client):
        self.client = client
        with open("users.json", "r") as file:
            self.users = json.load(file)
        with open(r"Information/roles_list.json", "r") as file:
            self.roles_list = json.load(file)

    '''@app_commands.command(name="web", description="test")
    async def web(self, ctx):
        but_next = Button(style=ButtonStyle.grey, label="Next", emoji="➡")
        but_exit = Button(style=ButtonStyle.red, label="Exit", emoji="✖")
        but_save = Button(style=ButtonStyle.blurple, label="Save", emoji="💾")
        but_cancel = Button(style=ButtonStyle.red, label="Cancel", emoji="✖")

        async def next_callback(interaction):
            await interaction.response.send_modal(ProfileModal())

        async def exit_callback(interaction):
            await interaction.response.send_message("www.ieeemcmaster.ca")

        async def save_callback(interaction):
            await interaction.response.send_message("www.ieeemcmaster.ca")

        async def cancel_callback(interaction):
            await interaction.response.send_message("www.ieeemcmaster.ca")

        but_next.callback = next_callback
        but_exit.callback = exit_callback
        but_save.callback = save_callback
        but_cancel.callback = cancel_callback

        view = discord.ui.View()
        view.add_item(but_next)
        view.add_item(but_exit)

        await ctx.response.send_message("Here:", view=view)'''

    @app_commands.command(name="edit", description="Edit's your profile")
    async def edit(self, ctx):
        if str(ctx.user.id) in self.users:
            modal = ProfileModal(ctx, ctx.command)
            await ctx.response.send_modal(modal)
        else:
            await ctx.response.send_message("You don't have a profile yet. Type `/register` to get started.", ephemeral=True)


async def setup(client):
    await client.add_cog(Test(client))
