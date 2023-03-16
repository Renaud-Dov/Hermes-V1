#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import re

import discord

from src import logs
from src.client.checks import is_thread
from src.other.db import get_ticket_nb
from src.utils import setup_logging

_log = setup_logging(__name__)


@is_thread()
async def rename(interaction: discord.Interaction, name: str):
    thread: discord.Thread = interaction.channel
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
