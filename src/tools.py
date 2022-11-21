from typing import Optional

import discord

from src.ConfigFormat import Config, ManagerFormat


async def create_private_channel(category: discord.CategoryChannel, student: discord.Member, name: str):
    """Creates a private channel for a student and an assistant"""
    channel = await category.create_text_channel(name=name)
    await channel.set_permissions(student, read_messages=True, send_messages=True)
    return channel


async def create_vocal_channel(category: discord.CategoryChannel, student: discord.Member, name: str):
    """Creates a private channel for a student and an assistant"""
    voice_channel = await category.create_voice_channel(name=name)
    await voice_channel.set_permissions(student, overwrite=discord.PermissionOverwrite(connect=True, speak=True,
                                                                                       view_channel=True,
                                                                                       use_voice_activation=True))
    return voice_channel


def find_manager_category(member: discord.Member, config: Config) -> Optional[ManagerFormat]:
    """Finds the category where the member is a manager"""
    managers = config.settings.managers
    for managers_category in managers:
        if member.id in managers_category.users:
            return managers_category
        for role in member.roles:
            if role.id in managers_category.roles:
                return managers_category
    return None


def find_tag(forum: discord.ForumChannel, tag_name: str):
    for tag in forum.available_tags:
        if tag.name == tag_name:
            return tag
    return None


async def find_ticket_from_logs(log_chan: discord.TextChannel, thread_id: str):
    async for message in log_chan.history(limit=100):
        if message.embeds and message.embeds[0].footer and message.embeds[0].footer.text.split(" ")[-1] == thread_id:
            return message
    return None
