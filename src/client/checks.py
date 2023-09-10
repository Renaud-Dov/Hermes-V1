#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import os

import discord
from discord import app_commands

from src.exceptions import NotAThread

ADMIN_ID =int(os.environ.get("ADMIN_ID",208480161421721600))

def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == ADMIN_ID

    return app_commands.check(predicate)


def is_thread():
    def predicate(interaction: discord.Interaction) -> bool:
        channel = interaction.channel
        if not channel or channel.type != discord.ChannelType.public_thread:
            raise NotAThread()
        return True

    return app_commands.check(predicate)
