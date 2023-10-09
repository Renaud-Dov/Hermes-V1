#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.engine import engine
from src.data.models import Ticket


async def link(interaction: discord.Interaction, id: int):
    """
    Link to the ticket
    @param interaction:
    @param id: ID of the ticket.
    @return:
    """
    with Session(engine) as session:
        ticket = session.execute(select(Ticket).where(Ticket.id == id)).scalar_one_or_none()
        if ticket is None:
            await interaction.response.send_message("Invalid ID", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{ticket.guild_id}/{ticket.thread_id}"))
        await interaction.response.send_message(f"Ticket {ticket.id}",view=view)
