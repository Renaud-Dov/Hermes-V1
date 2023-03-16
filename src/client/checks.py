#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord
from discord import app_commands

from src.exceptions import NotAThread


def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        print(interaction.user.id)
        return interaction.user.id == 2084801614217216001

    return app_commands.check(predicate)


def is_thread():
    def predicate(interaction: discord.Interaction) -> bool:
        channel = interaction.channel
        if not channel or channel.type != discord.ChannelType.public_thread:
            raise NotAThread()
        return True

    return app_commands.check(predicate)