from typing import Optional
import re
import discord
from discord.app_commands import Choice

from src import Embed, tools
from src.ConfigFormat import Config
from src.tools import find_tag


async def close(interaction: discord.Interaction, type: Optional[Choice[str]]):
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

    tag = tools.find_tag(thread.parent, forum.end_tag)
    if tag:
        await thread.add_tags(tag)

    await interaction.response.send_message("Marked as done", ephemeral=True)
    await channel.send(embed=Embed.doneEmbed(interaction.user, "Resolved" if not type else type.value, config))
    await thread.edit(archived=True)  # TODO: lock thread


async def rename(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel or channel.type != discord.ChannelType.public_thread:
        await interaction.response.send_message("This is not a thread!", ephemeral=True)
        return

    thread: discord.Thread = channel
    old_name = thread.name
    # keep [#NUMBER] at the beginning of the name
    match = re.match(r"(\[\d+\])", old_name)
    if match:
        name = match.group(1) + " " + name
    await thread.edit(name=name)
    await interaction.response.send_message(f"Renamed from `{old_name}` to `{name}`", ephemeral=True)


async def delete_thread(client: discord.Client, thread: discord.Thread):
    config_forum = Config("config/config.yaml").get_forum(thread.parent_id)
    if not config_forum:
        return

    embed = Embed.deletedThreadEmbed(thread)
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed)


async def thread_create(client: discord.Client, thread: discord.Thread):
    config_forum = Config("config/config.yaml").get_forum(thread.parent_id)
    if not config_forum:
        return

    await thread.edit(auto_archive_duration=10080)  # 7 days to archive
    embed = Embed.newThreadEmbed(thread)
    view = discord.ui.View()
    view.add_item(Embed.urlButton(thread.jump_url))
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed, view=view)

    await thread.join()

    if "Moulinette" in [tag.name for tag in thread.applied_tags]:
        await thread.send("Merci de préciser votre login et le tag de votre trace ci dessous./Please specify your "
                          "login and the tag of your trace below.")


async def update_thread(client: discord.Client, before: discord.Thread, after: discord.Thread):
    return None


async def thread_member_join(client: discord.Client, member: discord.Member):
    config = Config("config/config.yaml")
    config_forum = config.get_forum(member.thread.parent_id)
    if not config_forum or member.thread.archived:
        return
    category = tools.find_manager_category(member, config)
    if not category:
        return
    log_chan = client.get_channel(config_forum.webhook_channel)
    # find the message in the log channel
    async for message in log_chan.history(limit=100):
        if message.embeds and message.embeds[0].footer.text == f"Thread ID: {member.thread.id}":
            embed: discord.Embed = message.embeds[0]
            Embed.editEmbed(embed, member, "Joined")
            await message.edit(embed=embed)
            break