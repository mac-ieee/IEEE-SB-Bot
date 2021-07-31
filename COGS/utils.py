import discord
from discord.ext import commands
import discord_components.interaction
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType, component
import json
import asyncio
import validators
from COGS.info import Info
from COGS.club import ClubActivities


class Utilities(commands.Cog, description="Utilities :tools:"):
    editable_cmds = {}

    def __init__(self, client):
        self.client = client
        self.info = Info(self.client)
        self.editable_cmds = {"Profile": ClubActivities.profile}
        self.editable_cmds.update(self.info.new_cmds)

    async def edit_group(self, ctx, cat, group):
        async def timeout():
            print("Someone took too long to respond")
            edit_embed.set_footer(text="No response received. COMMAND TERMINATED.")
            edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name, value=self.info.roles_list[cat][group][param], inline=False)
            edit_embed.title = group
            await message.edit(embed=edit_embed, components=[])

        params = {"Thumbnail": self.info.roles_list[cat][group]["Thumbnail"],
                  "Logo": self.info.roles_list[cat][group]['Logo'],
                  "Description": self.info.roles_list[cat][group]["Description"]}

        # Init Embed
        edit_embed = discord.Embed(title=f"Editing: {group}", colour=0X2072AA)
        edit_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        edit_embed.set_thumbnail(url=self.info.roles_list[cat][group]["Thumbnail"])
        edit_embed.add_field(name="THUMBNAIL:", value=params["Thumbnail"], inline=False)
        edit_embed.add_field(name="LOGO:", value=params["Logo"], inline=False)
        edit_embed.add_field(name="DESCRIPTION:", value=params["Description"], inline=False)
        but_next = Button(style=ButtonStyle.grey, label="Next", emoji="➡")
        but_exit = Button(style=ButtonStyle.red, label="Exit", emoji="✖")
        but_save = Button(style=ButtonStyle.blue, label="Save", emoji="💾")
        but_cancel = Button(style=ButtonStyle.red, label="Cancel", emoji="✖")
        message = await ctx.send(embed=edit_embed)

        for i, param in enumerate(params):
            cancel_save = True
            while cancel_save:
                edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name,
                                        value=params[param].join(["```fix\n", "\n```"]), inline=False)
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
                                edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name, value=params[param], inline=False)
                                await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed)

                                cancel_save, bad_response = False, False
                            # Terminates Command
                            elif payload.component.label == "Exit":
                                edit_embed.set_footer(text="COMMAND TERMINATED.")
                                edit_embed.title = group
                                edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name,
                                                        value=self.info.roles_list[cat][group][param].join(["", ""]), inline=False)
                                await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed,
                                                      components=[])
                                return True
                        elif type(payload) == discord_components.message.ComponentMessage:
                            payload.content = payload.content.strip()
                            if param == "Thumbnail":
                                if not validators.url(payload.content):
                                    edit_embed.set_footer(text="ERROR: Invalid URL!")
                                    break
                                else:
                                    edit_embed.set_thumbnail(url=payload.content.strip())
                            elif param == "Logo" and payload.content.startswith("\\"):
                                payload.content = payload.content[1:]

                            bad_response = False
                            edit_embed.set_footer(text=f"Save changes to {param}?")
                            edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name, value=f"```diff\n- {params[param]}\n+ {payload.content}\n```", inline=False)
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
                                    self.info.roles_list[cat][group][param] = payload.content.strip()
                                    edit_embed.set_footer(text=f"Changes made to {param} saved successfully.")
                                    cancel_save = False
                                # Does nothing, loops the editing for the same profile parameter
                                elif but_res.component.label == "Cancel":
                                    edit_embed.set_footer(text="")
                                    edit_embed.set_thumbnail(url=params["Thumbnail"])
                                await but_res.respond(type=InteractionType.UpdateMessage, embed=edit_embed)

            edit_embed.set_field_at(index=i, name=edit_embed.fields[i].name, value=self.info.roles_list[cat][group][param], inline=False)
            edit_embed.title = group
        await message.edit(embed=edit_embed, components=[])
        return False

    async def edit_leader(self, ctx, cat, group, leader):
        async def timeout():
            print("Someone took too long to respond")
            edit_embed.set_footer(text="No response received. COMMAND TERMINATED.")
            edit_embed.set_field_at(index=0, name="DESCRIPTION",
                                    value=self.info.roles_list[cat][group]["Leaders"][leader]["Description"],
                                    inline=False)
            edit_embed.title = f"{group} {leader}"
            await message.edit(embed=edit_embed, components=[])

        # Init Embed
        edit_embed = discord.Embed(title=f"Editing: {group} {leader}", colour=0X2072AA)
        edit_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        edit_embed.add_field(name="DESCRIPTION", value=self.info.roles_list[cat][group]["Leaders"][leader]["Description"])
        but_save = Button(style=ButtonStyle.blue, label="Save", emoji="💾")
        but_cancel = Button(style=ButtonStyle.red, label="Cancel", emoji="✖")
        message = await ctx.send(embed=edit_embed)

        cancel_save = True
        # Loop profile parameter editing if user cancels on saving. Maybe they made a typo.
        while cancel_save:
            edit_embed.set_field_at(index=0, name="DESCRIPTION", value=self.info.roles_list[cat][group]["Leaders"][leader]["Description"].join(["```fix\n", "\n```"]))
            await message.edit(embed=edit_embed, components=[[but_save, but_cancel]])

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
                    edit_embed.title = f"{group} {leader}"
                    edit_embed.set_field_at(index=0, name="DESCRIPTION",
                                            value=self.info.roles_list[cat][group]["Leaders"][leader][
                                                "Description"])
                    # Save reaction continues editing process, if more edits are queue
                    if payload.component.label == "Save":
                        edit_embed.set_footer(text=f"No changes were made to DESCRIPTION.")
                        cancel_save = False
                        await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed, components=[])
                    # Terminates Command
                    elif payload.component.label == "Cancel":
                        edit_embed.set_footer(text="COMMAND TERMINATED.")
                        await payload.respond(type=InteractionType.UpdateMessage, embed=edit_embed, components=[])
                        return True

                elif type(payload) == discord_components.message.ComponentMessage:
                    payload.content = payload.content.strip()
                    edit_embed.set_footer(text=f"Save changes to DESCRIPTION?")
                    edit_embed.set_field_at(index=0, name="DESCRIPTION",
                                            value=f"```diff\n- {self.info.roles_list[cat][group]['Leaders'][leader]['Description']}\n+ {payload.content}\n```", inline=False)
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
                            self.info.roles_list[cat][group]["Leaders"][leader]["Description"] = payload.content.strip()
                            edit_embed.set_footer(text=f"Changes made to DESCRIPTION saved successfully.")
                            cancel_save = False
                        # Does nothing, loops the editing for the same profile parameter
                        elif but_res.component.label == "Cancel":
                            edit_embed.set_footer(text="")
                        await but_res.respond(type=InteractionType.UpdateMessage, embed=edit_embed)

            edit_embed.set_field_at(index=0, name="DESCRIPTION",
                                    value=self.info.roles_list[cat][group]["Leaders"][leader]["Description"], inline=False)
            edit_embed.title = f"{group} {leader}"
        await message.edit(embed=edit_embed, components=[])
        return False

    # Ping
    @commands.command(description="Pings the bot and returns the latency")
    async def ping(self, ctx):
        pingEmbed = discord.Embed(title="Ping", colour=0X2072AA)
        pingEmbed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        pingEmbed.add_field(name="Pong!", value=f"Latency: {round(self.client.latency * 1000)}ms  :ping_pong:")
        await ctx.send(embed=pingEmbed)

    # Clear
    @commands.command(aliases=["prune", "purge"],
                      description="Deletes multiple messages (up to 1000).\n"
                                  "If no value is specified, 1 message will be deleted by default.",
                      usage="<integer>",
                      brief="clear\nclear 10",
                      help="User: Exec Role\nBot: Manage Messages")
    @commands.has_role("Exec")
    async def clear(self, ctx, arg_num=1):
        if arg_num > 1000 or arg_num < 1:
            await ctx.send(f"{ctx.author.mention}  You can only delete 1 - 1000 messages")
        else:
            await ctx.channel.purge(limit=1)
            await ctx.channel.purge(limit=arg_num)

    @commands.command(hidden=True)
    async def test(self, ctx):
        but = Button(style=ButtonStyle.red, label="FUCKING KYS", emoji="🔥")
        mymsg = await ctx.send("What Should I do?", components=[
            [Button(style=ButtonStyle.grey, label="IDC KYS"),
             Button(style=ButtonStyle.blue, label="KYS"),
             but,
             Button(style=ButtonStyle.green, label="KYS Please", disabled=True)]
        ])

        but_res = await self.client.wait_for("button_click", check=lambda user: user.author == ctx.author)
        print(type(but_res))
        print(but_res)
        if but_res.component.label == "FUCKING KYS":
            but.disabled = True
            await but_res.respond(type=InteractionType.UpdateMessage, content="I died", components=[but_res.components])

    @commands.command(description="Edits stuff. Use `-edit` to show a list of editables",
                      usage="<Main Arg.> <Sub Arg.> <Sub Arg.>",
                      brief="edit chapter computer\nedit chapter computer chair",
                      help="Bot: Manage Messages")
    async def edit(self, ctx, cat=None, group=None, *, leader=None):
        with open(r"Information/roles_list.json", "r") as file:
            self.info.roles_list = json.load(file)

        indexed_info = ({"Profile": {
            "Name": None, "Email": None, "Program": None, "Year": None, "About": None}})
        indexed_info.update(self.info.roles_list)

        if cat:
            match = False
            # Filter cat with indexed list
            for c in indexed_info:
                if cat.lower() in self.editable_cmds[c].aliases or cat.lower() in c.lower():
                    cat, match = c, True
                    break
            if match and len(indexed_info[cat]) == 1:
                group, leader, match = cat, group, True
            if not match:
                return await ctx.reply(f"\"{cat}\" is not a recognisable option")
            elif group:
                match = False
                # Filter groups
                for g in indexed_info[cat]:
                    if group.lower() in g.lower():
                        group, match = g, True
                        break
                if not match:
                    return await ctx.reply(f"\"{group}\" is not a recognisable option in \"{cat}\"")
                elif leader:
                    match = False
                    # Filter leaders
                    for l in indexed_info[cat][group]["Leaders"]:
                        if leader.lower() in l.lower():
                            leader, match = l, True
                            break
                    if not match:
                        return await ctx.reply(f"\"{leader}\" is not a recognisable option in \"{cat} > {group}\"")

            if cat == "Profile":
                with open("users.json", "r") as file:
                    self.info.users = json.load(file)

                if str(ctx.author.id) in self.info.users:
                    await self.info.edit_prof(ctx, str(ctx.author.id), group)
                    with open("users.json", "w") as file:
                        json.dump(self.info.users, file, indent=4)
                else:
                    await ctx.reply("You don't have a profile yet. Type `-register` to get started.")

            elif leader:
                with open(r"Information/roles_list.json", "r") as file:
                    self.info.roles_list = json.load(file)

                await self.edit_leader(ctx, cat, group, leader)
                with open(r"Information/roles_list.json", "w") as file:
                    json.dump(self.info.roles_list, file, indent=4)
            elif group:
                with open(r"Information/roles_list.json", "r") as file:
                    self.info.roles_list = json.load(file)

                await self.edit_group(ctx, cat, group)
                with open(r"Information/roles_list.json", "w") as file:
                    json.dump(self.info.roles_list, file, indent=4)
            elif cat:
                await ctx.reply(
                    "Exactly what are you trying to edit? Please try again. See \"-edit\" for a list of editables.")

        else:
            desc = f"Turquoise are valid arguments\n```bash\n"
            profile_params = f", ".join([param for param in indexed_info['Profile']])
            desc += f"\"Profile\":\n\t\"{profile_params}\"\n\n"
            main_params = f", ".join([leader for leader in indexed_info['Main Branch']['Main Branch']['Leaders']])
            desc += f"\"Main\":\n\t\"{main_params}\"\n\n"
            chapter_params = f"\n\t".join(
                [f"{chapter}:\n\t\t{', '.join([leader for leader in indexed_info['Chapter'][chapter]['Leaders']])}" for
                 chapter in indexed_info['Chapter']])
            desc += f"Chapter:\n\t\"{chapter_params}\"\n\n"
            comm_params = f"\n\t".join(
                [f"{comm}:\n\t\t{', '.join([leader for leader in indexed_info['Committee'][comm]['Leaders']])}" for
                 comm in indexed_info['Committee']])
            desc += f"Committee:\n\t\"{comm_params}\"\n"
            desc += f"```"

            edit_embed = discord.Embed(title="Edit Options", description=desc, colour=0X2072AA)
            edit_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=edit_embed)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** You need to be an **Exec** to clear messages")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}  **ERROR:** Incorrect usage")
        else:
            await ctx.send(f"{ctx.author.mention}  **UNKNOWN ERROR:** Please try again later")


def setup(client):
    client.add_cog(Utilities(client))
