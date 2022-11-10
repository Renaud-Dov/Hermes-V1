import discord


async def create_private_channel(category: discord.CategoryChannel, student: discord.Member, name: str):
    """Creates a private channel for a student and an assistant"""
    channel = await category.create_text_channel(name=name)
    await channel.set_permissions(student, read_messages=True, send_messages=True)
    return channel


async def create_vocal_channel(category: discord.CategoryChannel, student: discord.Member, name: str):
    """Creates a private channel for a student and an assistant"""
    voice_channel = await category.create_voice_channel(name=name)
    await voice_channel.set_permissions(student, speak=True)
    return voice_channel
