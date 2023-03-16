#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from typing import Optional

import discord

from src import logs
from src.config import Config
from src.other import Embed
from src.other.tools import find_ticket_from_logs
from src.other.types import status_converter, TypeClose


async def close_all(interaction: discord.Interaction, forum: discord.ForumChannel, tag: int, reason: Optional[str]):
    config = Config("config/config.yaml")
    forum_config = config.get_forum(forum.id)
    if not forum_config:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return
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
