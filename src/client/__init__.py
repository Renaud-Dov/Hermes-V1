#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import os
from typing import List, Optional

import discord
from discord import app_commands
from discord.app_commands import Command
from jsonschema.exceptions import ValidationError

from src.config import Config, ExtraCommand
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
        self.configs: List[Config] = []
        self.__load_configs()

        # add update command

        self.tree.add_command(
            Command(name="update", description="Update commands (Admin only)", callback=self.updateCommands),
            guild=discord.Object(id=1033684799912677388))

    def __load_configs(self):
        # scan all files in config directory, and load them
        files = os.listdir("config")
        self.configs = []  # reset configs
        for file in files:
            try:
                config = Config(f"config/{file}")
                self.configs.append(config)
                _log.info(f"Loaded config file {file}")
            except ValidationError as e:
                _log.error(f"Error while loading config file {file}: {e.message}")
                continue
        _log.info(f"Loaded {len(self.configs)} config files")

    async def __update_config_commands(self):
        # update commands
        for config in self.configs:
            await self.update_guild_command(config)

    async def on_ready(self):
        _log.info(f'{self.user} has connected to Discord!')
        await self.tree.sync(guild=discord.Object(id=1033684799912677388))
        commands = await self.tree.fetch_commands()
        _log.info(f"Global commands available: {', '.join([f'{command.name}' for command in commands])}")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="les dieux"))

    async def updateCommands(self, interaction: discord.Interaction):
        await self.tree.sync()

        old_configs = [config.file_name for config in self.configs]
        self.__load_configs()

        # compare old configs with new ones:
        new_configs = [config.file_name for config in self.configs]
        diff_configs = list(set(old_configs) - set(new_configs))

        await self.__update_config_commands()

        if diff_configs:
            await interaction.response.send_message(
                f"Updated commands and configuration, but some configs are missing from last update: {', '.join(diff_configs)}")
        else:
            await interaction.response.send_message("Updated all commands and configuration")

    ############################
    #  Events
    ############################

    async def on_thread_create(self, thread: discord.Thread):
        _log.debug("Event on_thread_create triggered")
        await events.on_thread_create(self, thread)

    async def on_thread_delete(self, thread: discord.Thread):
        _log.debug(f"Event on_thread_delete triggered")
        await events.on_thread_delete(self, thread)

    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        _log.debug(f"Event on_thread_update triggered")
        await events.on_thread_update(self, before, after)

    async def on_thread_member_join(self, thread_member: discord.ThreadMember):
        _log.debug(f"Event on_thread_member_join triggered")
        await events.on_thread_member_join(self, thread_member)

    def add_commands(self, commands):
        for command in commands:
            if 'guilds' in command:
                guilds = [discord.Object(id=guild) for guild in command['guilds']]
                self.tree.add_command(command['command'], guilds=guilds)
            else:
                self.tree.add_command(command['command'])

    def get_config(self, guild_id: int):
        res = next((config for config in self.configs if config.meta.guild_id == guild_id), None)
        if res is None:
            raise ValueError(f"Config for guild {guild_id} not found")
        return res

    async def update_guild_command(self, config):
        guild = discord.Object(id=config.meta.guild_id)
        self.tree.clear_commands(guild=guild)
        for command in config.extra_commands:
            def create_callback(cmd: ExtraCommand):
                async def callback(interaction: discord.Interaction):
                    if cmd.hidden:
                        await interaction.response.send_message("Done", ephemeral=True)
                        await interaction.followup.send(content=cmd.message, embeds=cmd.embeds)
                    else:
                        await interaction.response.send_message(cmd.message, embeds=cmd.embeds, ephemeral=False)

                return callback

            callback_func = create_callback(command)

            self.tree.add_command(
                Command(name=command.name, description=command.description, callback=callback_func),
                guild=discord.Object(id=config.meta.guild_id))

        if config.meta.guild_id == 1033684799912677388:
            self.tree.add_command(
                Command(name="update", description="Update commands (Admin only)", callback=self.updateCommands),
                guild=discord.Object(id=1033684799912677388))
        await self.tree.sync(guild=guild)
        _log.info(f"Updated commands for guild {config.meta.name}")
