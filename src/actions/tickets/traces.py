#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from typing import List

import discord

from src import logs
from src.domain.entity.guildConfig import TraceTag
from src.other import Modal, tools
from src.other.tools import find_ticket_from_logs
from src.utils import setup_logging

_log = setup_logging(__name__)


async def trace_ticket(interaction: discord.Interaction, tag: str):
    config = interaction.client.get_config(interaction.guild_id)
    tags_list: List[TraceTag] = config.get_open_tag_tickets()
    name_tags = [tag.tag for tag in tags_list]
    if tag not in name_tags:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(name_tags), ephemeral=True)
        return
    config_trace: TraceTag = config.get_trace_tag(tag)
    groups_allowed = config_trace.allowed.roles
    users_allowed = config_trace.allowed.users
    user_roles = [role.id for role in interaction.user.roles]
    if not (set(groups_allowed).intersection(user_roles) or interaction.user.id in users_allowed):
        await interaction.response.send_message(
            "You are not allowed to create a ticket in this category. Please choose one of the following: " + ", ".join(
                name_tags), ephemeral=True)
        return
    await interaction.response.send_modal(Modal.AskQuestion(tag,config_trace))


async def __close_trace_ticket(interaction: discord.Interaction, config_ticket: TraceTag):
    log_chan = interaction.client.get_channel(config_ticket.webhook_channel)
    thread = interaction.channel
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:  # keep a copy of the ticket in the log channel
        try:
            log_thread = await log_chan.create_thread(name=thread.name, message=message, auto_archive_duration=10080)
        except discord.app_commands.errors.CommandInvokeError:
            await interaction.response.send_message(
                "I can't create a thread in the log channel, please contact an administrator.", ephemeral=True)
            # get thread from the log channel
        await tools.copy_thread_content(thread, log_thread)

    await thread.delete()
    logs.closed_trace_ticket(interaction.user, thread.id, config_ticket.tag)


async def close_trace_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    config = interaction.client.get_config(interaction.guild_id)
    tags_list = config.get_open_tag_tickets()
    for tag in tags_list:
        if tag.category_channel == channel.category_id:
            await __close_trace_ticket(interaction, tag)
            return
    await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
