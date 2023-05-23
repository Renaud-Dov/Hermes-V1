#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src import logs
from src.client import checks, HermesClient
from src.other import Embed


@checks.is_thread()
async def delete_ticket(client: HermesClient, thread: discord.Thread):
    config_forum = client.config.get_forum(thread.parent_id)
    if not config_forum:
        return
    embed = Embed.deletedThreadEmbed(thread)
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed)

    logs.deleted_ticket(thread.id, thread.name, thread.owner)
