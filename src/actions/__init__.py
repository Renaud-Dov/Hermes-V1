#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import discord

import src.actions.links
from src import logs
from src.actions import tickets
from src.config import Config, TicketFormat
from src.other import Embed
from src.other.tools import find_ticket_from_logs
from src.other.types import TypeStatusTicket


async def thread_member_join(client: discord.Client, thread: discord.Thread, member: discord.Member):
    config = Config("config/config.yaml")
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum or thread.archived:
        return
    category = config.find_manager_category(member)
    if not category:
        return
    log_chan = client.get_channel(config_forum.webhook_channel)
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:
        embed: discord.Embed = message.embeds[0]
        Embed.editEmbed(embed, member, TypeStatusTicket.Joined)
        await message.edit(embed=embed)


async def sendTrace(interaction: discord.Interaction, login: str, tag: str):
    log_chan = interaction.client.get_channel(1040188840557682740)
    if not log_chan:
        await interaction.response.send_message("I can't find the log channel, please contact an administrator.",
                                                ephemeral=True)
        return

    await log_chan.send(f"%{login}%\n{tag}")
    await interaction.response.send_message(f"Trace `{login}` `{tag}` sent to the staff team.")


async def close_trace_ticket(interaction: discord.Interaction, config_ticket: TicketFormat):
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
