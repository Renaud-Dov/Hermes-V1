import asyncio
import logging
from typing import Optional
import re
import discord

from src import Embed, tools, logs
from src.ConfigFormat import Config
from src.tools import find_ticket_from_logs
from src.types import TypeStatusTicket, TypeClose, status_converter


async def close(interaction: discord.Interaction, type: TypeClose, reason: str = None):
    thread: discord.Thread = interaction.channel
    if not thread or thread.type != discord.ChannelType.public_thread or thread.locked:
        await interaction.response.send_message("This is not a opened thread!", ephemeral=True)
        return

    config = Config("config/config.yaml")
    forum = config.get_forum(thread.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    log_chan = interaction.client.get_channel(forum.webhook_channel)
    # find the message in the log channel
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:
        embed: discord.Embed = message.embeds[0]
        status = status_converter(type)
        Embed.editEmbed(embed, interaction.user, status)
        view = discord.ui.View()
        view.add_item(Embed.urlButton(thread.jump_url))
        view.add_item(Embed.statusButton(status))
        await message.edit(embed=embed)

    tag = tools.find_tag(thread.parent, forum.end_tag)
    if tag:
        await thread.add_tags(tag)

    response_embed = Embed.doneEmbed(interaction.user, type, config, reason)
    if type == TypeClose.Resolve or type == TypeClose.Duplicate or type == TypeClose.ForceResolve:
        await interaction.response.send_message("Marked as done", ephemeral=True)
        await thread.send(embed=response_embed)
        if type == TypeClose.Resolve:
            await thread.owner.send(embed=Embed.reopenEmbed(thread, interaction.user), view=Embed.ReopenView())
        await thread.edit(archived=True, locked=True)
    elif type == TypeClose.Delete:
        await thread.owner.send(embed=response_embed)
        log_msg = await log_chan.send(embed=Embed.deletedThreadEmbed(thread, interaction.user, reason))
        # create a new thread in response to the log message
        log_thread = await log_msg.create_thread(name=thread.name, auto_archive_duration=0)

        content = "```\n"
        async for message in thread.history(limit=None,oldest_first=True):
            # if content is too long, make sure to send 2000 characters at a time
            line= f"{message.author.name}#{message.author.discriminator}: {message.content}\n"
            content += line + "\n"
            if len(content) > 2000:
                # keep max 2000 characters
                content_left = content[:1900]
                content_left += "```"
                await log_thread.send(content_left)
                content = "```\n" + content[1900:]

        content += "```"
        await log_thread.send(content)
        await thread.delete()


    logs.close_ticket(interaction.user, type, thread.id, reason)


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
    logs.renamed_ticket(interaction.user, thread.id, old_name, name)


async def delete_thread(client: discord.Client, thread: discord.Thread):
    config_forum = Config("config/config.yaml").get_forum(thread.parent_id)
    if not config_forum:
        return

    embed = Embed.deletedThreadEmbed(thread)
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed)

    logs.deleted_ticket(thread.id, thread.name, thread.owner)


async def thread_create(client: discord.Client, thread: discord.Thread):
    config_forum = Config("config/config.yaml").get_forum(thread.parent_id)
    if not config_forum:
        return

    await thread.edit(auto_archive_duration=10080)  # 7 days to archive
    embed = Embed.newThreadEmbed(thread, TypeStatusTicket.Created)
    view = discord.ui.View()
    view.add_item(Embed.urlButton(thread.jump_url))
    view.add_item(Embed.statusButton(TypeStatusTicket.Created))
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed, view=view)

    await thread.join()

    if "Moulinette" in [tag.name for tag in thread.applied_tags]:
        await asyncio.sleep(0.5)
        await thread.send("Merci de préciser votre login et le tag de votre trace ci dessous./Please specify your "
                          "login and the tag of your trace below.")

    logs.new_ticket(thread.id, thread.name, thread.owner)


async def update_thread(client: discord.Client, before: discord.Thread, after: discord.Thread):
    config_forum = Config("config/config.yaml").get_forum(after.parent_id)
    if not config_forum:
        return

    if "Moulinette" in [tag.name for tag in after.applied_tags] \
            and not "Moulinette" in [tag.name for tag in before.applied_tags]:
        await asyncio.sleep(0.5)
        await after.send("Merci de préciser votre login et le tag de votre trace ci dessous./Please specify your "
                         "login and the tag of your trace below.")


async def thread_member_join(client: discord.Client, thread: discord.Thread, member: discord.Member):
    config = Config("config/config.yaml")
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum or thread.archived:
        return
    category = tools.find_manager_category(member, config)
    if not category:
        return
    log_chan = client.get_channel(config_forum.webhook_channel)
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:
        embed: discord.Embed = message.embeds[0]
        Embed.editEmbed(embed, member, TypeStatusTicket.Joined)
        await message.edit(embed=embed)


async def reopen_ticket(interaction: discord.Interaction):
    message = interaction.message
    if not message.embeds:
        await interaction.response.send_message("You have deleted embed, I can't find related data anymore.")
        return
    ids = message.embeds[0].footer.text.split(" ")[-2:]
    id_forum = int(ids[0])
    channel = interaction.client.get_channel(id_forum)
    if not channel:
        await interaction.response.send_message("I can't find the forum channel, please contact an administrator.")
        return
    id_thread = int(ids[1])
    thread = await channel.guild.fetch_channel(id_thread)
    if not thread:
        await interaction.response.send_message("I can't find the ticket, please contact an administrator.")
        return
    config = Config("config/config.yaml")
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum:
        return
    await thread.edit(archived=False, locked=False, auto_archive_duration=10080)
    await thread.remove_tags(tools.find_tag(thread.parent, config_forum.end_tag))
    await message.delete()
    await thread.send(f"**The Ticket has been reopened by {interaction.user.mention}.**")

    log_chan = interaction.client.get_channel(config_forum.webhook_channel)
    embed = Embed.newThreadEmbed(thread, TypeStatusTicket.Recreated)
    view = discord.ui.View()
    view.add_item(Embed.urlButton(thread.jump_url))
    view.add_item(Embed.statusButton(TypeStatusTicket.Recreated))
    await log_chan.send(embed=embed, view=view)
    await interaction.user.send("Ticket has been reopened.")

    logs.reopen_ticket(interaction.user, thread.id, thread.name, thread.owner)


async def close_all(interaction: discord.Interaction,forum: discord.ForumChannel, tag: int, reason: Optional[str]):
    config = Config("config/config.yaml")
    forum_config = config.get_forum(forum.id)
    if not forum_config:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return
    if tag == 0:
        await interaction.response.send_message("Tags: " + ", ".join([f"`{tag.id} {tag.name}`" for tag in forum.available_tags]), ephemeral=True)
        return

    tag = forum.get_tag(tag)
    if not tag:
        await interaction.response.send_message("This tag does not exist!", ephemeral=True)
        return

    threads = [thread for thread in forum.threads if tag in thread.applied_tags]
    if not threads:
        await interaction.response.send_message("There is no thread with this tag!", ephemeral=True)
        return
    log_chan = interaction.client.get_channel(forum_config.webhook_channel)
    await interaction.response.send_message("Marked as done", ephemeral=True)
    for thread in threads:
        message = await find_ticket_from_logs(log_chan, str(thread.id))
        if message:
            embed: discord.Embed = message.embeds[0]
            status = status_converter(TypeClose.Resolve)
            Embed.editEmbed(embed, interaction.user, status)
            view = discord.ui.View()
            view.add_item(Embed.urlButton(thread.jump_url))
            view.add_item(Embed.statusButton(status))
            await message.edit(embed=embed)

            response_embed = Embed.doneEmbed(interaction.user, TypeClose.Resolve, config, reason)
            await thread.send(embed=response_embed)
            await thread.edit(archived=True, locked=True)
            logs.close_ticket(interaction.user, TypeClose.Resolve, thread.id, reason)