#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.client import HermesClient
from src.data.engine import engine
from src.data.models import Ticket, TicketParticipant
from src.other import Embed
from src.other.tools import find_ticket_from_logs
from src.utils import setup_logging

_log = setup_logging(__name__)


async def ask_title(interaction: discord.Interaction):
    """
    Ask ticket creator to give explicit title to his ticket
    @param interaction: interaction
    """
    thread: discord.Thread = interaction.channel
    if not thread or thread.type != discord.ChannelType.public_thread or thread.locked:
        await interaction.response.send_message("This is not a opened thread!", ephemeral=True)
        return
    config = interaction.client.get_config(interaction.guild_id)
    forum = config.get_forum(thread.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    if config.get_manager_category(interaction.user) is None:
        await interaction.response.send_message("You are not allowed to use this command! You must be a manager.",
                                                ephemeral=True)
        return

    channel = interaction.channel
    await interaction.response.send_message("Sending message...", ephemeral=True)
    embed = discord.Embed(title="Invalid title!", description=
    "Le titre de votre ticket ne suit pas les règles. **Merci de donner un titre explicite à votre ticket sans quoi aucune aide ne pourra vous être apportée.**\n\n" +
    "The title of your ticket does not follow the rules. **Please give an explicit title to your ticket otherwise no help can be provided to you.**",
                          color=discord.Color.red())

    await channel.send(thread.owner.mention, embed=embed)
    _log.info(f"AskTitle command used by {interaction.user} with on thread {thread.id}")
