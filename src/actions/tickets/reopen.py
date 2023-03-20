#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src import logs
from src.config import config
from src.other import tools, Embed
from src.other.types import TypeStatusTicket


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
