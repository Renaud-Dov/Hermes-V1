#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src.other.db import get_id_ticket


async def link(interaction: discord.Interaction, id: int):
    """
    Link to the ticket
    @param interaction:
    @param id: ID of the ticket.
    @return:
    """
    ticket_id = get_id_ticket(id)
    if ticket_id == -1:
        await interaction.response.send_message("Invalid ID", ephemeral=True)
        return
    await interaction.response.send_message(f"https://discord.com/channels/{interaction.guild.id}/{ticket_id}")
