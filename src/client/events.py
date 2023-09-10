#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import logging

import discord

from src.actions import tickets
from src.exceptions import ConfigNotFound

logger = logging.getLogger(__name__)


async def on_thread_create(client: discord.Client, thread: discord.Thread):
    logger.debug(f"Thread created: {thread.name}")
    try:
        await tickets.create_ticket(client, thread)
    except ConfigNotFound as e:
        logger.error(e.message)


async def on_thread_delete(client: discord.Client, thread: discord.Thread):
    logger.debug(f"Thread deleted: {thread.name}")
    try:
        await tickets.delete_ticket(client, thread)
    except ConfigNotFound as e:
        logger.error(e.message)


async def on_thread_update(client: discord.Client, before: discord.Thread, after: discord.Thread):
    try:
        await tickets.update_ticket(client, before, after)
    except ConfigNotFound as e:
        logger.error(e.message)


async def on_message(client: discord.Client, message: discord.Message):
    try:
        await tickets.on_message(client, message)
    except ConfigNotFound as e:
        logger.error(e.message)
