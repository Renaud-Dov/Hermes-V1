#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import re

import discord

from src import logs
from src.db import get_ticket_nb
from src.types import TypeClose


async def close(interaction: discord.Interaction, type: TypeClose, reason: str = None):
    pass


async def rename(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel or channel.type != discord.ChannelType.public_thread:
        await interaction.response.send_message("This is not a thread!", ephemeral=True)
        return

    thread: discord.Thread = channel
    old_name = thread.name
    # keep [#NUMBER] at the beginning of the name
    match = re.match(r"(\[\d+\])", old_name)
    if match:
        name = match.group(1) + " " + name
    else:
        name = f"[{get_ticket_nb(thread.id)}] {name}"
    await thread.edit(name=name)
    await interaction.response.send_message(f"Renamed from `{old_name}` to `{name}`", ephemeral=True)
    logs.renamed_ticket(interaction.user, thread.id, old_name, name)
