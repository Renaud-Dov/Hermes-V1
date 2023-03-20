#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import logging

import discord

from src.actions import tickets

logger = logging.getLogger(__name__)


async def on_thread_create(client: discord.Client, thread: discord.Thread):
    logger.debug(f"Thread created: {thread.name}")
    await tickets.create_ticket(client, thread)


async def on_thread_delete(client: discord.Client, thread: discord.Thread):
    logger.debug(f"Thread deleted: {thread.name}")
    await tickets.delete_ticket(client, thread)


async def on_thread_update(client: discord.Client, before: discord.Thread, after: discord.Thread):
    await tickets.update_ticket(client, before, after)


async def on_thread_member_join(client: discord.Client, thread_member: discord.ThreadMember):
    await tickets.join_ticket(client, thread_member)
