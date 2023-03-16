#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src import actions
from src.config import TicketFormat, config
from src.other import Modal


async def trace_ticket(interaction: discord.Interaction, category: str):
    tags_list = config.get_open_tag_tickets()
    if category not in tags_list:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
        return
    config_ticket = config.tickets[category]
    await interaction.response.send_modal(Modal.AskQuestion(category, config_ticket))


async def close_trace_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    tags_list = config.get_open_tag_tickets()
    for tag in tags_list:
        config_ticket: TicketFormat = config.tickets[tag]
        if config_ticket.category_channel == channel.category_id:
            await actions.close_trace_ticket(interaction, config_ticket)
            return
    await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
