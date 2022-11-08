import logging
import os
from typing import Optional

import discord
from discord import app_commands
from discord.app_commands import Choice
from src.ConfigFormat import Config
from src import Embed

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print("Bot is ready!")
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="les élèves"))


@tree.command(guild=discord.Object(id=999964493608144907), name="update", description="Update commands")
async def updateCommands(interaction: discord.Interaction):
    await tree.sync(guild=discord.Object(id=999964493608144907))
    await tree.sync()
    await interaction.response.send_message("Updated commands")


@tree.command(name="done", description="Mark a ticket as resolved")
@app_commands.choices(type=[Choice(name="Resolved", value="Resolved"), Choice(name="Duplicate", value="Duplicate")])
@app_commands.describe(type="Mark a ticket as resolved or duplicate (default: Resolved)")
@app_commands.describe(reason="Reason for closing the ticket")
async def done(interaction: discord.Interaction, type: Optional[Choice[str]], reason: Optional[str]):
    channel = interaction.channel
    if not channel or channel.type != discord.ChannelType.public_thread:
        await interaction.response.send_message("This is not a thread!", ephemeral=True)
        return

    config = Config("config.yaml")
    forum = config.get_forum(channel.parent_id)
    if not forum:
        await interaction.response.send_message("This thread is not linked to a forum!", ephemeral=True)
        return

    thread: discord.Thread = channel
    log_chan = client.get_channel(forum.webhook_channel)
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
    await channel.send(embed=Embed.doneEmbed(interaction.user, "Resolved" if not type else type.value, reason))


@client.event
async def on_thread_create(thread: discord.Thread):
    print("Thread created")
    config = Config("config.yaml")
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum:
        return

    await thread.edit(auto_archive_duration=10080)  # 7 days to archive
    embed = Embed.newThreadEmbed(thread)
    view = Embed.newThreadView(thread.jump_url)
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed, view=view)

    await thread.join()


@client.event
async def on_thread_member_join(member: discord.ThreadMember):
    config = Config("config.yaml")
    config_forum = config.get_forum(member.thread.parent_id)
    if not config_forum or member.thread.archived:
        return
    if member.id not in config.settings.managers: return
    log_chan = client.get_channel(config_forum.webhook_channel)
    # find the message in the log channel
    async for message in log_chan.history(limit=100):
        if message.embeds and message.embeds[0].footer.text == f"Thread ID: {member.thread.id}":
            embed: discord.Embed = message.embeds[0]
            Embed.editEmbed(embed, client.get_user(member.id), "Joined")
            await message.edit(embed=embed)
            break


# @block.error
# @unblock.error
# @me.error
# async def block_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     if isinstance(error, app_commands.CommandOnCooldown):
#         await interaction.response.send_message(f"**Please wait {int(error.retry_after)} seconds before trying again**",
#                                                 ephemeral=True)
#     else:
#         logger.exception(error)
#         await interaction.response.send_message("**Something went wrong. Please retry later**", ephemeral=True)

try:
    client.run(os.environ.get("DISCORD_TOKEN"))
except Exception as e:
    logger.exception(e)
    exit(1)
