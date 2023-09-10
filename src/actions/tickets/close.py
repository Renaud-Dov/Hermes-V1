#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from datetime import datetime
from typing import Optional

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import logs
from src.data.engine import engine
from src.data.models import Ticket, TicketLog, TicketTag
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType
from src.other import tools, Embed
from src.other.Embed import newThreadEmbed
from src.other.tools import find_ticket_from_logs
from src.domain.entity.close_type import CloseType
from src.utils import url_to_message


async def close(interaction: discord.Interaction, type: Optional[CloseType] = CloseType.Resolve, reason: str = None):
    thread: discord.Thread = interaction.channel
    if not thread or thread.type != discord.ChannelType.public_thread or thread.locked:
        await interaction.response.send_message("This is not a opened thread!", ephemeral=True)
        return
    config = interaction.client.get_config(interaction.guild_id)
    forum = config.get_forum(thread.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    session = Session(engine)
    ticket = session.execute(select(Ticket).where(Ticket.thread_id == str(thread.id))).scalar_one_or_none()
    if not ticket:
        await interaction.response.send_message("This thread is not linked to a ticket!", ephemeral=True)
        return

    time = datetime.utcnow()
    ticket.closed_at = time  # update closed_at in database
    ticket.updated_at = time  # update updated_at in database
    log_chan = interaction.client.get_channel(forum.webhook_channel)
    # find the message in the log channel
    message = await url_to_message(client=interaction.client, url=ticket.webhook_message_url)
    if message:
        embed: discord.Embed = newThreadEmbed(thread, Status.CLOSED)
        await message.edit(embed=embed)

    tags_name = [tag.name for tag in thread.applied_tags]  # get tags to remove

    if tag := tools.find_tag(thread.parent, forum.closing_tag):  # if the closing tag is present, add it
        await thread.add_tags(tag)

    response_embed = Embed.closingEmbed(interaction.user, type, config, reason)
    match type:
        case CloseType.Resolve | CloseType.ForceResolve | CloseType.Duplicate:
            await interaction.response.send_message("Marked as done", ephemeral=True)
            await thread.send(embed=response_embed)
            if type == CloseType.Resolve:  # send embed to user with reopen button
                await thread.owner.send(embed=Embed.closedPMEmbed(ticket, thread, interaction.user),
                                        view=Embed.ReopenView())
            await thread.edit(archived=True, locked=True)  # archive thread and lock it
            logs.close_ticket(interaction.user, type, thread.id, reason)  # log the action
            ticket.status = Status.CLOSED  # update ticket status in database
            log = TicketLog(ticket=ticket, kind=LogType.CLOSED_TICKET, by=interaction.user.id, message=reason, at=time)
            session.add(log)

        case CloseType.Delete:
            ticket.status = Status.DELETED  # update ticket status in database
            await thread.owner.send(embed=response_embed)  # send embed to user
            log_msg = await log_chan.send(embed=Embed.deletedThreadEmbed(thread, interaction.user, reason))
            # create a new thread in response to the log message
            log_thread = await log_msg.create_thread(name=thread.name, auto_archive_duration=0)
            await tools.copy_thread_content(thread, log_thread)
            await thread.delete()
            logs.deleted_ticket(ticket_id=ticket.id, name=thread.name, user=interaction.user)
            log = TicketLog(ticket=ticket, kind=LogType.DELETED_TICKET, by=interaction.user.id, message=reason, at=time)
            session.add(log)

    for tag in tags_name:
        ticket.tags.append(TicketTag(tag=tag))  # add tags to ticket in database

    session.commit()

# async def close_all(interaction: discord.Interaction, forum: discord.ForumChannel, tag: str = "0",
#                     reason: Optional[str] = None):
#     config = interaction.client.get_config(interaction.guild_id)
#     forum_config = config.get_forum(forum.id)
#     if not forum_config:
#         await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
#         return
#     if not tag.isdigit():
#         await interaction.response.send_message("This tag does not exist!", ephemeral=True)
#         return
#     tag = int(tag)
#     if tag == 0:
#         await interaction.response.send_message(
#             "Tags: " + ", ".join([f"`{tag.id} {tag.name}`" for tag in forum.available_tags]), ephemeral=True)
#         return
#
#     tag = forum.get_tag(tag)
#     if not tag:
#         await interaction.response.send_message("This tag does not exist!", ephemeral=True)
#         return
#
#     threads = [thread for thread in forum.threads if tag in thread.applied_tags]
#     if not threads:
#         await interaction.response.send_message("There is no thread with this tag!", ephemeral=True)
#         return
#     log_chan = interaction.client.get_channel(forum_config.webhook_channel)
#     await interaction.response.send_message("Marked as done", ephemeral=True)
#     for thread in threads:
#         message = await find_ticket_from_logs(log_chan, str(thread.id))
#         if message:
#             embed: discord.Embed = message.embeds[0]
#             status = status_converter(CloseType.Resolve)
#             Embed.editEmbed(embed, interaction.user, status)
#             view = discord.ui.View()
#             view.add_item(Embed.urlButton(thread.jump_url))
#             view.add_item(Embed.statusButton(status))
#             await message.edit(embed=embed)
#
#             response_embed = Embed.closingEmbed(interaction.user, CloseType.Resolve, config, reason)
#             await thread.send(embed=response_embed)
#             await thread.edit(archived=True, locked=True)
#             logs.close_ticket(interaction.user, CloseType.Resolve, thread.id, reason)
