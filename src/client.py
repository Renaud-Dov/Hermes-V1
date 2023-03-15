#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import logging
import os
import uuid

import discord
from discord import app_commands
from discord.app_commands import AppCommandError, Command

from src import logs
from src.actions import links, tickets

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

logger = logging.getLogger('discord')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')
    commands = await tree.fetch_commands()
    logger.debug(f"Global commands available: {', '.join([f'{command.name}' for command in commands])}")
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="les dieux"))


async def errors(interaction: discord.Interaction, error: AppCommandError):
    id_err = uuid.uuid4()
    embed = discord.Embed(title="λάθος",
                          description="An error occurred. Please try again later or contact an assistant",
                          color=discord.Color.red())
    embed.add_field(name="ID Error", value=id_err, inline=False)
    embed.set_footer(text="μην τα σπας όλα")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.NotFound:
        try:
            await interaction.user.send(embed=embed)
        except discord.errors.Forbidden:
            pass
    except discord.errors.InteractionResponded:
        pass
    logs.error(interaction.user, error, id_err)


async def updateCommands(interaction: discord.Interaction):
    await tree.sync(guild=discord.Object(id=interaction.guild_id))
    await tree.sync()
    await interaction.response.send_message("Updated commands")


tree.error(errors)

commands = [
    {'command': Command(name="google", description="What do you know about `Let me google that for you`?",
                        callback=links.google.google)},
    {'command': Command(name="intra", description="Get the intra link", callback=links.intra.intra)},
    {'command': Command(name="git", description="Get the git link", callback=links.git.git)},
    {'command': Command(name="close", description="Mark a ticket as resolved", callback=tickets.close)},
    {'command': Command(name="rename", description="Rename a ticket", callback=tickets.rename)},
    {'command': Command(name="link", description="Link to another ticket", callback=links.link.link)},
    {'command': Command(name="update", description="Update commands (Admin only)", callback=updateCommands),
     'guilds': [999964493608144907, 1033684799912677388]},

]
for command in commands:
    if 'guilds' in command:
        guilds = [discord.Object(id=guild) for guild in command['guilds']]
        tree.add_command(command['command'], guilds=guilds)
    else:
        tree.add_command(command['command'])

try:
    client.run(DISCORD_TOKEN)
except Exception as e:
    logger.exception(e)
    exit(1)
