import logging
import os
from typing import Optional

import discord
from discord import app_commands
from discord.app_commands import Choice
from src.ConfigFormat import Config, TicketFormat
from src import Embed, Modal, actions, tools
from src.tools import create_vocal_channel

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


@tree.command(guilds=[discord.Object(id=999964493608144907),
                      discord.Object(id=1033684799912677388)],
              name="update", description="Update commands")
async def updateCommands(interaction: discord.Interaction):
    await tree.sync(guild=discord.Object(id=interaction.guild_id))
    await tree.sync()
    await interaction.response.send_message("Updated commands")


@tree.command(name="ticket", description="Open a ticket")
@app_commands.describe(category="Category tag assistants told you to use")
async def open_new_ticket(interaction: discord.Interaction, category: str):
    config = Config("config/config.yaml")

    tags_list = config.get_open_tag_tickets()
    if category not in tags_list:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
        return
    config_ticket = config.tickets[category]
    await interaction.response.send_modal(Modal.AskQuestion(category, config_ticket))


@tree.command(name="add_vocal", description="Add a vocal channel to a ticket")
@app_commands.describe(student="Student to add to vocal channel")
async def add_vocal(interaction: discord.Interaction, category: str, student: discord.Member):
    channel = interaction.channel
    config = Config("config/config.yaml")
    tags_list = config.get_open_tag_tickets()
    if category not in tags_list:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
        return
    config_ticket: TicketFormat = config.tickets[category]
    if config_ticket.category_channel != channel.category_id:
        await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
        return
    voice_channel = await create_vocal_channel(client.get_channel(config_ticket.category_channel), student,
                                               interaction.channel.name)
    await interaction.response.send_message(f"Added a vocal channel to the ticket! {voice_channel.mention}")


async def remove_ticket(interaction: discord.Interaction, category: str):
    channel = interaction.channel

    config = Config("config/config.yaml")
    tags_list = config.get_open_tag_tickets()
    if category not in tags_list:
        await interaction.response.send_message(
            "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
        return

    config_ticket: TicketFormat = config.tickets.get(category)
    if not config_ticket or config_ticket.category_channel != channel.category_id:
        await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
        return
    # find vocal channel with same name if exists
    vocal_channel = discord.utils.get(interaction.channel.category.voice_channels, name=channel.name)
    if vocal_channel is not None:
        await vocal_channel.delete()
    await channel.delete()
    await interaction.response.send_message("Removed the ticket!", ephemeral=True)

    log_chan = client.get_channel(config_ticket.webhook_channel)
    await log_chan.send(f"Ticket {channel.name} has been close and deleted by {interaction.user.mention}")


# @tree.command(name="remove", description="Remove text and vocal channels from a ticket")


############################################
#               LINKS                      #
############################################
@tree.command(name="rename", description="Rename a ticket")
@app_commands.describe(name="New name of the ticket")
async def rename(interaction: discord.Interaction, name: str):
    await actions.rename(interaction, name)


@tree.command(name="git", description="Link to git survival guide")
async def git(interaction: discord.Interaction):
    await interaction.response.send_message("https://moodle.cri.epita.fr/mod/page/view.php?id=18488")


@tree.command(name="intra", description="Link to Forge Intra")
async def intra(interaction: discord.Interaction):
    await interaction.response.send_message("https://intra.forge.epita.fr/epita-prepa-acdc")


@tree.command(name="abel")
async def abel(interaction: discord.Interaction, name: str):
    await interaction.response.send_message("done", ephemeral=True)
    if interaction.user.id != 208480161421721600:
        return

    await interaction.channel.send(name)


############################################
#              FORUM TICKETS               #
############################################
@tree.command(name="close", description="Mark a ticket as resolved")
@app_commands.choices(type=[Choice(name="Resolved", value="Resolved"), Choice(name="Duplicate", value="Duplicate")])
@app_commands.describe(type="Mark a ticket as resolved or duplicate (default: Resolved)")
async def close(interaction: discord.Interaction, type: Optional[Choice[str]]):
    await actions.close(interaction, type)


@client.event
async def on_thread_create(thread: discord.Thread):
    await actions.thread_create(client, thread)


@client.event
async def on_thread_delete(thread: discord.Thread):
    logger.info(f"Thread {thread.name}{thread.id} has been deleted")
    await actions.delete_thread(client, thread)


@client.event
async def on_thread_remove(thread: discord.Thread):
    logger.info(f"Thread {thread.name}{thread.id} has been removed")
    await actions.delete_thread(client, thread)


@client.event
async def on_thread_update(before: discord.Thread, after: discord.Thread):
    logger.info(f"Thread {before.name}{before.id} has been updated")
    await actions.update_thread(client, before, after)


@client.event
async def on_thread_member_join(member: discord.ThreadMember):
    logger.info(f"Thread {member.thread.name}{member.thread.id} has a new member {member.user.name}{member.user.id}")
    await actions.thread_member_join(client, member)


try:
    client.run(os.environ.get("DISCORD_TOKEN"))
except Exception as e:
    logger.exception(e)
    exit(1)
