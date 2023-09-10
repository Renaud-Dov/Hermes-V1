#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import logs
from src.data.engine import engine
from src.data.models import Ticket, TicketLog
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType
from src.other import tools, Embed
from src.other.Embed import newThreadEmbed
from src.utils import url_to_message


async def reopen_ticket(interaction: discord.Interaction):
    message = interaction.message
    if not message.embeds:
        await interaction.response.send_message("You have deleted embed, I can't find related data anymore.")
        return
    ticket_id = next((field.value for field in message.embeds[0].fields if field.name == "Ticket ID"), None)
    if not ticket_id:
        await interaction.response.send_message("I can't find the related ticket, please contact an administrator.")
        return
    session = Session(engine)
    ticket = session.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
    channel = interaction.client.get_channel(int(ticket.forum_id))
    if not channel:
        await interaction.response.send_message("I can't find the forum channel, please contact an administrator.")
        return
    thread = await channel.guild.fetch_channel(int(ticket.thread_id))
    if not thread:
        await interaction.response.send_message("I can't find the ticket, please contact an administrator.")
        return


    config = interaction.client.get_config(thread.guild.id)
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum:
        return
    await thread.edit(archived=False, locked=False, auto_archive_duration=10080)
    await thread.remove_tags(tools.find_tag(thread.parent, config_forum.closing_tag))
    await message.delete()
    await thread.send(f"**The Ticket has been reopened by {interaction.user.mention}.**")

    log_chan = interaction.client.get_channel(config_forum.webhook_channel)

    # find the message in the log channel
    message = await url_to_message(client=interaction.client, url=ticket.webhook_message_url)
    if message:
        embed: discord.Embed = newThreadEmbed(thread, Status.OPEN)
        await message.edit(embed=embed)
    await interaction.user.send(f"Ticket has been reopened.")

    ticket.closed_at = None
    ticket.reopened_times += 1
    ticket.updated_at = datetime.utcnow()
    ticket.status = Status.IN_PROGRESS
    ticket.tags = []

    log = TicketLog(ticket=ticket, kind=LogType.REOPENED_TICKET, by=interaction.user.id)
    session.add(log)

    session.commit()

    logs.reopen_ticket(interaction.user, thread.id, thread.name, thread.owner)
