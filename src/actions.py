from typing import Optional
import re
import discord
from discord.app_commands import Choice

from src import Embed
from src.ConfigFormat import Config


async def close(interaction: discord.Interaction, type: Optional[Choice[str]]):
    pass
    channel = interaction.channel
    if not channel or channel.type != discord.ChannelType.public_thread:
        await interaction.response.send_message("This is not a thread!", ephemeral=True)
        return

    config = Config("config/config.yaml")
    forum = config.get_forum(channel.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    thread: discord.Thread = channel
    log_chan = interaction.client.get_channel(forum.webhook_channel)
    # find the message in the log channel
    async for message in log_chan.history(limit=100):
        if message.embeds and message.embeds[0].footer.text == f"Thread ID: {thread.id}":
            embed: discord.Embed = message.embeds[0]
            Embed.editEmbed(embed, interaction.user, "Resolved" if not type else type.value)
            view = discord.ui.View()
            view.add_item(Embed.urlButton(thread.jump_url))
            await message.edit(embed=embed, view=view)
            break

    for tag in thread.parent.available_tags:  # find the tag to add
        if tag.name == forum.end_tag:
            await thread.add_tags(tag)
            break

    await interaction.response.send_message("Marked as done", ephemeral=True)
    await channel.send(embed=Embed.doneEmbed(interaction.user, "Resolved" if not type else type.value))
    await thread.edit(archived=True)


async def rename(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel or channel.type != discord.ChannelType.public_thread:
        await interaction.response.send_message("This is not a thread!", ephemeral=True)
        return

    thread: discord.Thread = channel
    old_name = thread.name
    # keep [#NUMBER] at the beginning of the name
    match = re.match(r"(\[#\d+\])", old_name)
    if match:
        name = match.group(1) + " " + name
    await thread.edit(name=name)
    await interaction.response.send_message(f"Renamed from `{old_name}` to `{name}`", ephemeral=True)
