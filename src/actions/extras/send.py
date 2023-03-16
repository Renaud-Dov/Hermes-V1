#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from typing import Optional

import discord

from src.client.checks import is_me


@is_me()
async def send_message(interaction: discord.Interaction, name: str, response: Optional[str] = None):
    await interaction.response.send_message("done", ephemeral=True)
    if response is None:
        await interaction.channel.send(name)
    else:
        # get message from response
        message: discord.Message = await interaction.channel.fetch_message(response)
        await message.reply(name)
