#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import discord
from discord import app_commands
from discord.app_commands import Command

from src.utils import setup_logging
from . import error, events

_log = setup_logging(__name__)


class HermesClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.tree.error(error.errors)

        # add update command

        self.tree.add_command(
            Command(name="update", description="Update commands (Admin only)", callback=self.updateCommands),
            guilds=[discord.Object(id=999964493608144907), discord.Object(id=1033684799912677388)])

    async def on_ready(self):
        _log.info(f'{self.user} has connected to Discord!')
        commands = await self.tree.fetch_commands()
        _log.info(f"Global commands available: {', '.join([f'{command.name}' for command in commands])}")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="les dieux"))

    async def updateCommands(self, interaction: discord.Interaction):
        await self.tree.sync(guild=discord.Object(id=interaction.guild_id))
        await self.tree.sync()
        await interaction.response.send_message("Updated commands")

    ############################
    #  Events
    ############################

    async def on_thread_create(self, thread: discord.Thread):

        await events.on_thread_create(self, thread)

    @staticmethod
    async def on_thread_delete(thread: discord.Thread):
        await events.on_thread_delete(thread)

    @staticmethod
    async def on_thread_update(before: discord.Thread, after: discord.Thread):
        await events.on_thread_update(before, after)

    @staticmethod
    async def on_thread_member_join(thread_member: discord.ThreadMember):
        await events.on_thread_member_join(thread_member)

    def add_commands(self, commands):
        for command in commands:
            if 'guilds' in command:
                guilds = [discord.Object(id=guild) for guild in command['guilds']]
                self.tree.add_command(command['command'], guilds=guilds)
            else:
                self.tree.add_command(command['command'])
