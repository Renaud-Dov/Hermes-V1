#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import os

import client
from client import commands

client = client.HermesClient()

client.add_commands(commands.commands)

try:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    client.run(DISCORD_TOKEN)
except Exception as e:
    client.logger.exception(e)
    exit(1)

# @tree.command(name="trace", description="Create a trace ticket")
# @app_commands.describe(category="Category tag assistants told you to use")
# @app_commands.guild_only()
# async def trace_ticket(interaction: discord.Interaction, category: str):
#     config = Config("../config/config.yaml")
#
#     tags_list = config.get_open_tag_tickets()
#     if category not in tags_list:
#         await interaction.response.send_message(
#             "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
#         return
#     config_ticket = config.tickets[category]
#     await interaction.response.send_modal(Modal.AskQuestion(category, config_ticket))
#
#
# @tree.command(name="close_trace", description="Close a trace ticket")
# @app_commands.guild_only()
# async def close_trace_ticket(interaction: discord.Interaction):
#     channel = interaction.channel
#     config = Config("../config/config.yaml")
#     tags_list = config.get_open_tag_tickets()
#     for tag in tags_list:
#         config_ticket: TicketFormat = config.tickets[tag]
#         if config_ticket.category_channel == channel.category_id:
#             await actions.close_trace_ticket(interaction, config_ticket)
#             return
#     await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
#
#
# @tree.command(name="add_vocal", description="Add a vocal channel to a ticket")
# @app_commands.describe(student="Student to add to vocal channel")
# @app_commands.guild_only()
# async def add_vocal(interaction: discord.Interaction, category: str, student: discord.Member):
#     channel = interaction.channel
#     config = Config("../config/config.yaml")
#     tags_list = config.get_open_tag_tickets()
#     if category not in tags_list:
#         await interaction.response.send_message(
#             "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
#         return
#     config_ticket: TicketFormat = config.tickets[category]
#     if config_ticket.category_channel != channel.category_id:
#         await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
#         return
#     voice_channel = await create_vocal_channel(client.get_channel(config_ticket.category_channel), student,
#                                                interaction.channel.name)
#     await interaction.response.send_message(f"Added a vocal channel to the ticket! {voice_channel.mention}")
#
#
# async def remove_ticket(interaction: discord.Interaction, category: str):
#     channel = interaction.channel
#
#     config = Config("../config/config.yaml")
#     tags_list = config.get_open_tag_tickets()
#     if category not in tags_list:
#         await interaction.response.send_message(
#             "Invalid category. Please choose one of the following: " + ", ".join(tags_list), ephemeral=True)
#         return
#
#     config_ticket: TicketFormat = config.tickets.get(category)
#     if not config_ticket or config_ticket.category_channel != channel.category_id:
#         await interaction.response.send_message("This channel is not linked to a ticket!", ephemeral=True)
#         return
#     # find vocal channel with same name if exists
#     vocal_channel: discord.VoiceChannel = await discord.utils.get(interaction.channel.category.voice_channels,
#                                                                   name=channel.name)
#     if vocal_channel is not None:
#         await vocal_channel.delete()
#     await channel.delete()
#     await interaction.response.send_message("Removed the ticket!", ephemeral=True)
#
#     log_chan = client.get_channel(config_ticket.webhook_channel)
#     await log_chan.send(f"Ticket {channel.name} has been close and deleted by {interaction.user.mention}")


# @tree.command(name="remove", description="Remove text and vocal channels from a ticket")


############################################
#               LINKS                      #
############################################
# @tree.command(name="rename", description="Rename a ticket")
# @app_commands.describe(name="New name of the ticket")
# @app_commands.guild_only()
# async def rename(interaction: discord.Interaction, name: str):
#     await actions.rename(interaction, name)
#
#
#
# @tree.command(name="google", description="What do you know about `Let me google that for you`?")
# @app_commands.describe(query="Query to search")
# async def google(interaction: discord.Interaction, query: str, message: Optional[str]):
#     # transform query in url format
#     query = urllib.parse.quote(query)
#
#     r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers={
#         "Authorization": f"Bearer {BITLY_TOKEN}"
#     }, data=json.dumps({
#         "long_url": f"https://letmegooglethat.com/?q={query}"
#     }))
#     if not r.ok:
#         await interaction.response.send_message(f"Error while creating link: {r.json()}", ephemeral=True)
#         return
#     r = r.json()
#
#     if message is None:
#         message = ""
#     else:
#         message += " "
#     await interaction.response.send_message("Send message", ephemeral=True)
#     await interaction.channel.send(message + r["link"], suppress_embeds=True)
#
#     logger.info(f"Google command used by {interaction.user} with query {query} : {r['link']}")
#
#
# # @tree.command(name="rules", description="Reminders of the rules")
# # @app_commands.guild_only()
# # async def rules(interaction: discord.Interaction):
# #     await interaction.response.send_message("done", ephemeral=True)
# #     if interaction.user.id != 208480161421721600:
# #         return
# #     await interaction.channel.send(embeds=[Embed.rulesEmbedFr(), Embed.rulesEmbedEn()])
#
#
# # @tree.command(name="link", description="Link to another ticket")
# # @app_commands.describe(id="ID of the ticket")
# # async def link(interaction: discord.Interaction, id: int):
# #     ticket_id = get_id_ticket(id)
# #     if ticket_id == -1:
# #         await interaction.response.send_message("Invalid ID", ephemeral=True)
# #         return
# #     await interaction.response.send_message(f"https://discord.com/channels/{interaction.guild.id}/{ticket_id}")
#
#
#
#
# ############################################
# #              FORUM TICKETS               #
# ############################################
# @tree.command(name="close", description="Mark a ticket as resolved")
# @app_commands.describe(type="Mark a ticket as resolved or duplicate (default: Resolved)")
# @app_commands.describe(reason="Reason for closing the ticket (Optional)")
# @app_commands.guild_only()
# async def close(interaction: discord.Interaction, type: Optional[TypeClose], reason: Optional[str]):
#     actions.tickets.close()
#     await actions.close(interaction, type if type else TypeClose.Resolve, reason)
#
#
# @tree.command(name="send_ticket")
# @app_commands.guild_only()
# async def close2(interaction: discord.Interaction, login: str, tag: str):
#     await actions.sendTrace(interaction, login, tag)
#
#
# @tree.command(name="close_all", description="Mark all tickets with a specific tag as resolved")
# @app_commands.describe(reason="Reason for closing the ticket (Optional)")
# @app_commands.guild_only()
# async def close_all(interaction: discord.Interaction, forum: discord.ForumChannel, tag: Optional[str],
#                     reason: Optional[str]):
#     await actions.close_all(interaction, forum, int(tag or 0), reason)
#
#
# @client.event
# async def on_thread_create(thread: discord.Thread):
#     logger.debug(f"Thread{thread.id} has been create")
#     await actions.thread_create(client, thread)
#
#
# @client.event
# async def on_thread_delete(thread: discord.Thread):
#     logger.debug(f"Thread {thread.name} {thread.id} has been deleted")
#     await actions.delete_thread(client, thread)
#
# @client.event
# async def on_thread_update(before: discord.Thread, after: discord.Thread):
#     await actions.update_thread(client, before, after)
#
#
# @client.event
# async def on_thread_member_join(thread_member: discord.ThreadMember):
#     member: discord.Member = thread_member.thread.guild.get_member(thread_member.id)
#     await actions.thread_member_join(client, thread_member.thread, member)
