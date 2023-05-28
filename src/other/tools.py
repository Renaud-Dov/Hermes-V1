#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

from typing import Optional

import discord


async def create_private_channel(category: discord.CategoryChannel, student: discord.Member,
                                 name: str) -> discord.TextChannel:
    """
    Creates a private channel for a student and all the assistants
    @param category: category where to create the channel
    @param student: student to add to the channel
    @param name: name of the channel
    @return: the created channel
    """
    channel = await category.create_text_channel(name=name, overwrites={
        student: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    })
    # await channel.set_permissions(student, read_messages=True, send_messages=True)
    return channel


async def create_vocal_channel(category: discord.CategoryChannel, student: discord.Member,
                               name: str) -> discord.VoiceChannel:
    """
    Creates a vocal channel for a student and an assistant
    @param category: category where to create the channel
    @param student: student to add to the channel
    @param name: name of the channel
    @return: the created channel
    """
    voice_channel = await category.create_voice_channel(name=name)
    await voice_channel.set_permissions(student,
                                        overwrite=discord.PermissionOverwrite(connect=True, speak=True,
                                                                              view_channel=True,
                                                                              use_voice_activation=True))
    return voice_channel


def find_tag(forum: discord.ForumChannel, tag_name: str) -> Optional[discord.ForumTag]:
    """
    Finds a tag by its name
    @param forum: Forum where to find the tag
    @param tag_name: Name of the tag
    @return: Tag or None
    """
    return next((tag for tag in forum.available_tags if tag.name == tag_name), None)


async def find_ticket_from_logs(log_chan: discord.TextChannel, thread_id: str) -> Optional[discord.Message]:
    """
    Finds a ticket from the logs
    @param log_chan: Channel where the logs are
    @param thread_id: ID of the thread
    @return: message of the ticket or None
    """
    async for message in log_chan.history(limit=100):
        if message.embeds and message.embeds[0].footer and message.embeds[0].footer.text.split(" ")[-1] == thread_id:
            return message
    return None
