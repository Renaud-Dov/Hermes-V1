#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord
from discord import app_commands


def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        print(interaction.user.id)
        return interaction.user.id == 2084801614217216001

    return app_commands.check(predicate)
