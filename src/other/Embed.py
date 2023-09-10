#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import datetime

import discord

from src.actions import tickets
from src.data.models import Ticket
from src.domain.entity.TicketStatus import Status
from src.domain.entity.guildConfig import Config
from src.domain.entity.close_type import CloseType


def urlButton(url: str) -> discord.ui.Button:
    """
    Create a button with a link
    @rtype: object
    @param url: Url of the link
    @return: Button
    """
    return discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=url)


class ReopenView(discord.ui.View):
    def __init__(self):
        """
        Init the view
        """
        super().__init__()
        self.timeout = 8 * 60 * 60  # 8 hours before the view times out

    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.green, emoji="🔓")
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await tickets.reopen_ticket(interaction)


def newThreadEmbed(thread: discord.Thread, status: Status):
    """
    Embed when a new thread is created
    @param thread: Thread
    @param status: Status of the thread
    @return: Embed
    """
    embed = discord.Embed(title=thread.name, color=discord.Color.orange())
    if thread.starter_message:
        embed.description = thread.starter_message.content
    embed.timestamp = thread.created_at

    match status:
        case Status.OPEN:
            status_field = f"🟢 {status.value}"
        case Status.CLOSED:
            status_field = f"🔴 {status.value}"
        case Status.IN_PROGRESS:
            status_field = f"🟡 {status.value}"
        case _:
            status_field = f"🟠 {status.value}"
    embed.add_field(name="Status", value=status_field)
    embed.set_author(name=thread.owner.display_name, icon_url=thread.owner.display_avatar)
    embed.set_footer(text=f"Thread ID: {thread.id}")

    if thread.applied_tags:
        embed.add_field(name="Tags", value="\n".join(
            [f"**{tag.name}**" + (f" {tag.emoji}" if tag.emoji else "") for tag in thread.applied_tags]))

    return embed


def closingEmbed(member: discord.Member, status: CloseType, config: Config, reason: str = None):
    """
    Embed when a ticket is closed
    @param member: Member who closed the ticket
    @param status: Status of the ticket
    @param config: Config of the bot
    @param reason: Reason of the close
    @return: Embed
    """
    embed = discord.Embed(title="Ticket has been closed by an assistant.", description=reason,
                          color=discord.Color.blue())
    if category := config.get_manager_category(member):
        embed.title = category.message

    match status:
        case CloseType.Duplicate:
            embed.colour = discord.Colour.red()
            embed.title = "This question has already been answered. Please check if your question is already answered " \
                          "before creating a new ticket."
        case CloseType.Delete:
            embed.colour = discord.Colour.red()
            embed.title = "This ticket has been deleted. Please check rules before creating a new ticket."

    embed.set_author(name=member.display_name, icon_url=member.display_avatar)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="If you have any further questions, please create a new ticket.")
    return embed


def newTraceEmbed(student: discord.Member, category_tag: str, login: str, question: str, channel: discord.TextChannel):
    """
    Create embed for new trace ticket
    @param student: Student who created the ticket
    @param category_tag: Category tag
    @param login: Login of the student
    @param question: Question of the student
    @param channel: Channel of the ticket
    @return: Embed
    """
    embed = discord.Embed(title="New ticket created", color=discord.Color.orange())
    embed.description = question
    embed.set_author(name=student.display_name, icon_url=student.display_avatar)
    embed.add_field(name="Category", value=category_tag)
    embed.add_field(name="Login", value=f"%{login}%")
    embed.set_footer(text=f"Ticket ID: {channel.id}")
    embed.timestamp = discord.utils.utcnow()
    return embed


def rulesTicketEmbed():
    """
    Create embed for rules of ticket
    @return: Embed
    """
    embed = discord.Embed(title="Règles relatives aux tickets privés", color=discord.Color.green())
    embed.description = """Tout ce qui est écrit dans ce channel est visible par les assistants, ainsi que les 
    modérateurs du serveur. Si vous souhaitez que votre question reste privée, merci de ne pas la poser ici.
    Le partage de code est autorisé, uniquement sur ce channel. Si vous souhaitez partager du code, merci de le mettre 
    dans un [code block](https://support.discord.com/hc/fr/articles/210298617) ou par fichier.
    
    Cordialement,
    L'équipe assistante."""
    return embed


def deletedThreadEmbed(thread: discord.Thread, member: discord.Member = None, reason: str = None):
    """
    Create embed for deleted thread
    @param thread: Thread
    @param member: Member who deleted the thread
    @param reason: Reason of the deletion
    @return: Embed
    """
    embed = discord.Embed(title="Ticket has been deleted", color=discord.Color.red())
    embed.description = reason
    if member:
        embed.set_author(name=member.display_name, icon_url=member.display_avatar)
    embed.add_field(name="Thread name", value=thread.name)
    embed.add_field(name="Thread Creator", value=thread.owner.mention)

    embed.timestamp = discord.utils.utcnow()
    return embed


def closedPMEmbed(ticket: Ticket,thread: discord.Thread, manager: discord.Member):
    """
    Create embed for closed thread in Private Message
    @param ticket: Ticket model in database
    @param thread: Thread
    @param manager: Member who reopen the thread
    @return: Embed
    """

    embed = discord.Embed(title="Your ticket has been closed", color=discord.Color.blue())
    embed.description = f"Your ticket {thread.mention} has been closed by {manager.mention}. " \
                        f"If you want to reopen it, please click on the button below."
    embed.set_author(name=manager.display_name, icon_url=manager.display_avatar)
    embed.add_field(name="Thread name", value=thread.name)
    embed.add_field(name="Time remaining to reopen", value=discord.utils.format_dt(discord.utils.utcnow() + datetime.timedelta(hours=8), style='R'))
    embed.timestamp = discord.utils.utcnow()
    embed.add_field(name="Ticket ID", value=ticket.id)
    embed.set_footer(text=f"Thread ID: {thread.parent.id} {thread.id}")
    return embed
