#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from typing import Optional

import discord

from src import logs
from src.other import tools, Embed
from src.other.tools import find_ticket_from_logs
from src.other.types import TypeClose, status_converter


async def close(interaction: discord.Interaction, type: Optional[TypeClose] = TypeClose.Resolve, reason: str = None):
    thread: discord.Thread = interaction.channel
    if not thread or thread.type != discord.ChannelType.public_thread or thread.locked:
        await interaction.response.send_message("This is not a opened thread!", ephemeral=True)
        return
    config = interaction.client.config
    forum = config.get_forum(thread.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    log_chan = interaction.client.get_channel(forum.webhook_channel)
    # find the message in the log channel
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:
        embed: discord.Embed = message.embeds[0]
        status = status_converter(type)
        Embed.editEmbed(embed, interaction.user, status)
        view = discord.ui.View()
        view.add_item(Embed.urlButton(thread.jump_url))
        view.add_item(Embed.statusButton(status))
        await message.edit(embed=embed)

    tag = tools.find_tag(thread.parent, forum.end_tag)
    if tag:
        await thread.add_tags(tag)

    response_embed = Embed.doneEmbed(interaction.user, type, config, reason)
    if type == TypeClose.Resolve or type == TypeClose.Duplicate or type == TypeClose.ForceResolve:
        await interaction.response.send_message("Marked as done", ephemeral=True)
        await thread.send(embed=response_embed)
        if type == TypeClose.Resolve:
            await thread.owner.send(embed=Embed.reopenEmbed(thread, interaction.user), view=Embed.ReopenView())
        await thread.edit(archived=True, locked=True)
        logs.close_ticket(interaction.user, type, thread.id, reason)
    elif type == TypeClose.Delete:
        await thread.owner.send(embed=response_embed)
        log_msg = await log_chan.send(embed=Embed.deletedThreadEmbed(thread, interaction.user, reason))
        # create a new thread in response to the log message
        log_thread = await log_msg.create_thread(name=thread.name, auto_archive_duration=0)

        content = "```\n"
        async for message in thread.history(limit=None, oldest_first=True):
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
        await log_thread.send(content)
        await thread.delete()


async def close_all(interaction: discord.Interaction, forum: discord.ForumChannel, tag: str = "0",
                    reason: Optional[str] = None):
    config = interaction.client.config
    forum_config = config.get_forum(forum.id)
    if not forum_config:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return
    if not tag.isdigit():
        await interaction.response.send_message("This tag does not exist!", ephemeral=True)
        return
    tag = int(tag)
    if tag == 0:
        await interaction.response.send_message(
            "Tags: " + ", ".join([f"`{tag.id} {tag.name}`" for tag in forum.available_tags]), ephemeral=True)
        return

    tag = forum.get_tag(tag)
    if not tag:
        await interaction.response.send_message("This tag does not exist!", ephemeral=True)
        return

    threads = [thread for thread in forum.threads if tag in thread.applied_tags]
    if not threads:
        await interaction.response.send_message("There is no thread with this tag!", ephemeral=True)
        return
    log_chan = interaction.client.get_channel(forum_config.webhook_channel)
    await interaction.response.send_message("Marked as done", ephemeral=True)
    for thread in threads:
        message = await find_ticket_from_logs(log_chan, str(thread.id))
        if message:
            embed: discord.Embed = message.embeds[0]
            status = status_converter(TypeClose.Resolve)
            Embed.editEmbed(embed, interaction.user, status)
            view = discord.ui.View()
            view.add_item(Embed.urlButton(thread.jump_url))
            view.add_item(Embed.statusButton(status))
            await message.edit(embed=embed)

            response_embed = Embed.doneEmbed(interaction.user, TypeClose.Resolve, config, reason)
            await thread.send(embed=response_embed)
            await thread.edit(archived=True, locked=True)
            logs.close_ticket(interaction.user, TypeClose.Resolve, thread.id, reason)
