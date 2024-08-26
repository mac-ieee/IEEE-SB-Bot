import discord
from discord.ext import commands
from COGS.info import Info
import json


class Settings(commands.Cog, description="Settings :gear:"):
    rr_channels = {}
    role_ids = [776270321313513486, 776270276920999946, 776270245383897148]

    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        with open(r"Information/rr_channels.json", "r") as file:
            self.rr_channels = json.load(file)

    @commands.command(aliases=["br"],
                      description="Toggles reaction roles for the current channel.",
                      help="User: Executives Role\nBot: Highest Role Possible")
    @commands.has_role("Executives")
    async def br_setup(self, ctx):
        # Compare current channel with the set channel
        channel = ctx.channel.id
        stored_channel = self.rr_channels["Chapter"]["ChannelID"]
        if channel == stored_channel:
            # Disable RR
            self.rr_channels["Chapter"]["ChannelID"] = ""
            with open(r"Information/rr_channels.json", "w") as file:
                json.dump(self.rr_channels, file, indent=4)
        else:
            # Enable RR for the new Channel
            self.rr_channels["Chapter"]["ChannelID"] = channel
            with open(r"Information/rr_channels.json", "w") as file:
                json.dump(self.rr_channels, file, indent=4)

        # make sure to set the guild ID here to whatever server you want the buttons in

    @commands.command()
    async def post(self, ctx: commands.Context):
        """A slash command to post a new view with a button for each role"""

        # timeout is None because we want this view to be persistent
        view = discord.ui.View(timeout=None)

        # loop through the list of roles and add a new button to the view for each role
        for role_id in self.role_ids:
            # get the role the guild by ID
            role = ctx.guild.get_role(role_id)
            view.add_item(RoleButton(role))

        await ctx.send("Click a button to assign yourself a role", view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        """This function is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons)
        it will be loaded and the bot will start watching for button clicks again.
        """

        # we recreate the view as we did in the /post command
        view = discord.ui.View(timeout=None)
        # make sure to set the guild ID here to whatever server you want the buttons in
        guild = self.client.get_guild(757373396362330149)
        for role_id in self.role_ids:
            role = guild.get_role(role_id)
            view.add_item(RoleButton(role))

            # add the view to the bot so it will watch for button interactions
            self.client.add_view(view)


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(
            label=role.name,
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: discord.Interaction):
        """This function will be called any time a user clicks on this button
        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that was created when the user clicked on the button
        """

        # figure out who clicked the button
        user = interaction.user
        # get the role this button is for (stored in the custom ID)
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # if this role doesn't exist, ignore
            # you can do some error handling here
            return

        # passed all checks
        # add the role and send a response to the uesr ephemerally (hidden to other users)
        if role not in user.roles:
            # give the user the role if they don't already have it
            await user.add_roles(role)
            await interaction.response.send_message(
                f"🎉 You have been given the role {role.mention}", ephemeral=True
            )
        else:
            # else, take the role from the user
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ The {role.mention} role has been taken from you", ephemeral=True
            )


async def setup(client):
    await client.add_cog(Settings(client))

