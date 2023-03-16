#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import logging

import discord

logger = logging.getLogger(__name__)


async def on_thread_create(self, thread: discord.Thread):
    print("Thread created")
    logger.info(f"Thread created: {thread.name}")


async def on_thread_delete(thread):
    print("Thread deleted")
    logger.info(f"Thread deleted: {thread.name}")
    return None


async def on_thread_update(before, after):
    return None


async def on_thread_member_join(thread_member):
    return None
