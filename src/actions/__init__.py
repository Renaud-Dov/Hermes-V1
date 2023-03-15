#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import asyncio
from typing import Optional

import discord
from discord import app_commands

import src.actions.links
from src import Embed, tools, logs
from src.actions import tickets
from src.client import tree
from src.config import Config, TicketFormat
from src.db import get_ticket_nb, add_ticket
from src.tools import find_ticket_from_logs
from src.types import TypeStatusTicket, TypeClose, status_converter


async def close(interaction: discord.Interaction, type: TypeClose, reason: str = None):
    return await tickets.close(interaction, type, reason)


async def rename(interaction: discord.Interaction, name: str):
    return await tickets.rename(interaction, name)


@tree.command(name="abel")
@app_commands.guild_only()
async def abel(interaction: discord.Interaction, name: str, response: Optional[str] = None):
    await interaction.response.send_message("done", ephemeral=True)
    if interaction.user.id != 208480161421721600:
        return
    if response is None:
        await interaction.channel.send(name)
    else:
        # get message from response
        message: discord.Message = await interaction.channel.fetch_message(response)
        await message.reply(name)


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
    config = Config("config/config.yaml")
    config_forum = config.get_forum(thread.parent_id)
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

    tag_id = config.get_week_practical_tag(thread)
    if tag_id:
        await thread.add_tags(thread.parent.get_tag(tag_id))
        await thread.send(f"Auto added tag {thread.parent.get_tag(tag_id).name}")

    if "Moulinette" in [tag.name for tag in thread.applied_tags]:
        await asyncio.sleep(0.5)
        await thread.send("Merci de préciser votre login et le tag de votre trace ci dessous./Please specify your "
                          f"login and the tag of your trace below. {thread.owner.mention}")

    add_ticket(thread.id, thread.owner_id)
    id_ticket = get_ticket_nb(thread.id)
    await thread.edit(name=f"[{id_ticket}] {thread.name}")

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
    category = config.find_manager_category(member)
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


async def close_all(interaction: discord.Interaction, forum: discord.ForumChannel, tag: int, reason: Optional[str]):
    config = Config("config/config.yaml")
    forum_config = config.get_forum(forum.id)
    if not forum_config:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return
    if tag == 0:
        await interaction.response.send_message(
            "Tags: " + ", ".join([f"`{tag.id} {tag.name}`" for tag in forum.available_tags]), ephemeral=True)
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


async def sendTrace(interaction: discord.Interaction, login: str, tag: str):
    log_chan = interaction.client.get_channel(1040188840557682740)
    if not log_chan:
        await interaction.response.send_message("I can't find the log channel, please contact an administrator.",
                                                ephemeral=True)
        return

    await log_chan.send(f"%{login}%\n{tag}")
    await interaction.response.send_message(f"Trace `{login}` `{tag}` sent to the staff team.")


async def close_trace_ticket(interaction: discord.Interaction, config_ticket: TicketFormat):
    log_chan = interaction.client.get_channel(config_ticket.webhook_channel)
    thread = interaction.channel
    message = await find_ticket_from_logs(log_chan, str(thread.id))
    if message:  # keep a copy of the ticket in the log channel
        try:
            log_thread = await log_chan.create_thread(name=thread.name, message=message, auto_archive_duration=10080)
        except discord.app_commands.errors.CommandInvokeError:
            await interaction.response.send_message(
                "I can't create a thread in the log channel, please contact an administrator.", ephemeral=True)
            # get thread from the log channel
        content = "```\n"
        async for message in thread.history(limit=None, oldest_first=True):
            # if message.author.bot:
            #     continue
            # if content is too long, make sure to send 2000 characters at a time
            line = f"{message.author.name}#{message.author.discriminator}: {message.content}\n"
            content += line + "\n"
            if len(content) > 2000:
                # keep max 2000 characters
                content_left = content[:1900]
                content_left += "```"
                await log_thread.send(content_left)
                content = "```\n" + content[1900:]

        content += "```"
        if content != "```\n```":  # if there is no content, don't send anything, it's useless
            await log_thread.send(content)
    await thread.delete()
    logs.closed_trace_ticket(interaction.user, thread.id, config_ticket.open_tag)
