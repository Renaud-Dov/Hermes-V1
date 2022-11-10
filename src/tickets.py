import discord


async def create_private_channel(category: discord.CategoryChannel, student: discord.Member, name: str):
    """Creates a private channel for a student and an assistant"""
    channel = await category.create_text_channel(name=name)
    await channel.set_permissions(student, read_messages=True, send_messages=True)
    return channel