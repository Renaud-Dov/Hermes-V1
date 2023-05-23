#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src.client import HermesClient
from src.other import Embed
from src.other.tools import find_ticket_from_logs
from src.other.types import TypeStatusTicket


async def join_ticket(client: HermesClient, thread_member: discord.ThreadMember):
    thread = thread_member.thread
    config = client.get_config(thread.guild.id)
    member: discord.Member = thread_member.thread.guild.get_member(thread_member.id)
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
