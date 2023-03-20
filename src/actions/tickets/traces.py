#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src import logs
from src.config import TicketFormat, config
from src.other import Modal
from src.other.tools import find_ticket_from_logs


async def trace_ticket(interaction: discord.Interaction, category: str):
    tags_list = config.get_open_tag_tickets()
    if category not in tags_list:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
        return
    config_ticket = config.tickets[category]
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
    logs.closed_trace_ticket(interaction.user, thread.id, config_ticket.open_tag)


async def close_trace_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    tags_list = config.get_open_tag_tickets()
    for tag in tags_list:
        config_ticket: TicketFormat = config.tickets[tag]
        if config_ticket.category_channel == channel.category_id:
            await __close_trace_ticket(interaction, config_ticket)
            return
    await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
