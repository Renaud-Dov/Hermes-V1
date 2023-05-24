#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import discord

from src import logs
from src.config import TicketFormat
from src.other import Modal
from src.other.tools import find_ticket_from_logs
from src.utils import setup_logging

_log = setup_logging(__name__)


async def trace_ticket(interaction: discord.Interaction, category: str):
    config = interaction.client.get_config(interaction.guild_id)
    tags_list = config.get_open_tag_tickets()
    name_tags = [tag.name for tag in tags_list]
    if category not in name_tags:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(name_tags), ephemeral=True)
        return
    config_ticket: TicketFormat = config.get_ticket(category)
    groups_allowed = config_ticket.groups
    user_roles = [role.id for role in interaction.user.roles]
    if not any(role in groups_allowed for role in user_roles):
        await interaction.response.send_message(
            "You are not allowed to create a ticket in this category. Please choose one of the following: " + ", ".join(
                name_tags), ephemeral=True)
        return
    await interaction.response.send_modal(Modal.AskQuestion(category, config_ticket))


async def __close_trace_ticket(interaction: discord.Interaction, config_ticket: TicketFormat):
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
        content = "```\n"
        async for message in thread.history(limit=None, oldest_first=True):
            # if message.author.bot:
            #     continue
            # if content is too long, make sure to send 2000 characters at a time
            line = f"{message.author.name}#{message.author.discriminator}: {message.content}\n"
            content += line + "\n"
            if len(content) > 2000:
                # keep max 2000 characters
                content_left = content[:1900]
                content_left += "```"
                await log_thread.send(content_left)
                content = "```\n" + content[1900:]

        content += "```"
        if content != "```\n```":  # if there is no content, don't send anything, it's useless
            await log_thread.send(content)
    await thread.delete()
    logs.closed_trace_ticket(interaction.user, thread.id, config_ticket.name)


async def close_trace_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    config = interaction.client.get_config(interaction.guild_id)
    tags_list = config.get_open_tag_tickets()
    for tag in tags_list:
        if tag.category_channel == channel.category_id:
            await __close_trace_ticket(interaction, tag)
            return
    await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
