#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord

from src.actions import tickets
from src.config import Config
from src.other.types import TypeStatusTicket, TypeClose


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
        self.timeout = None  # remove timeout

    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.green, emoji="🔓")
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await tickets.reopen_ticket(interaction)


def newThreadEmbed(thread: discord.Thread, status: TypeStatusTicket):
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
    if status.Created:
        embed.add_field(name="Status", value="Open 🟢")  # must be fist field
    elif status.Resolved:
        embed.add_field(name="Status", value="Reopened 🟢")  # must be fist field
    else:
        embed.add_field(name="Status", value="Other (Error)")
    embed.set_author(name=thread.owner.display_name, icon_url=thread.owner.display_avatar)
    if thread.applied_tags:
        embed.add_field(name="Tags", value="\n".join(
            [f"**{tag.name}**" + f" {tag.emoji}" if tag.emoji else "" for tag in thread.applied_tags]))

    embed.set_footer(text=f"Thread ID: {thread.id}")
    return embed


def doneEmbed(member: discord.Member, status: TypeClose, config: Config, reason: str = None):
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
    category = config.find_manager_category(member)
    if category:
        embed.title = category.msg

    match status:
        case TypeClose.Duplicate:
            embed.colour = discord.Colour.red()
            embed.title = "This question has already been answered. Please check if your question is already answered " \
                          "before creating a new ticket."
        case TypeClose.Delete:
            embed.colour = discord.Colour.red()
            embed.title = "This ticket has been deleted. Please check rules before creating a new ticket."

    embed.set_author(name=member.display_name, icon_url=member.display_avatar)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="If you have any further questions, please create a new ticket.")
    return embed


def editEmbed(embed: discord.Embed, member: discord.Member, status: TypeStatusTicket):
    """
    Edit embed to add status and member who did the action
    @param embed: Embed to edit
    @param member: Member who did the action
    @param status: Status of the ticket
    @return: None
    """
    match status:
        case TypeStatusTicket.Resolved:
            embed.set_field_at(0, name="Status", value="Done ✅")
            embed.colour = discord.Colour.light_gray()
        case TypeStatusTicket.Duplicate:
            embed.set_field_at(0, name="Status", value="Duplicate 🟡")
            embed.colour = discord.Colour.gold()
        case TypeStatusTicket.Closed:
            embed.set_field_at(0, name="Status", value="Closed 🔴")
            embed.colour = discord.Colour.red()
        case TypeStatusTicket.Joined:
            embed.set_field_at(0, name="Status", value="Joined 🟢")
            embed.colour = discord.Colour.orange()
        case TypeStatusTicket.Recreated:
            embed.set_field_at(0, name="Status", value="Recreated 🟢")
            embed.colour = discord.Colour.orange()
        case TypeStatusTicket.Created:
            embed.set_field_at(0, name="Status", value="Open 🟢")
            embed.colour = discord.Colour.orange()
        case TypeStatusTicket.Other:
            embed.set_field_at(0, name="Status", value="Other (Error)")
            embed.colour = discord.Colour.purple()
        case TypeStatusTicket.Deleted:
            embed.set_field_at(0, name="Status", value="Deleted 🔴")
            embed.colour = discord.Colour.red()

    for field in embed.fields:
        if field.name == "Action done by":
            embed.remove_field(embed.fields.index(field))
            break
    embed.add_field(name="Action done by", value=member.mention)

    embed.timestamp = discord.utils.utcnow()


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
    L'équipe ACDC."""
    return embed


def rulesEmbedFr():
    """
    Create embed for rules of ticket
    @return: Embed
    """
    embed = discord.Embed(title="Règles relatives aux tickets", color=discord.Color.yellow())
    embed.description = """Merci de respecter les règles suivantes :
    :one: Tout ce qui est écrit dans ce channel est visible par les assistants, ainsi que les modérateurs du serveur. Si vous souhaitez que votre question reste privée, merci de ne pas la poser ici.
    :two: Le partage de code est interdit, vos screens ne doivent pas contenir de code.
    :three: Regardez bien si votre question n'a pas déjà été posée avant de la poser, sinon elle sera considérée comme doublon.
    :four: Ne pas ping les assistants, ils vous répondront dès qu'ils le pourront. N'envoyez pas de messages privés aux assistants, à moins qu'ils vous l'aient demandé.
    :five: Spécifiez bien votre problème, et mettez un titre explicite à votre ticket, au cas où d'autres personnes se poseraient la même question.
    :six: Mettez un ou plusieurs tags à votre ticket, afin de faciliter la recherche de votre question par les assistants et les autres étudiants.
    :seven: Toute question en rapport aux tests ne sera pas traitée et sera supprimée.
    :eight: Les tps sont faits pour être réalisés sur le PIE (les machines de l'école). Dans ce sens, tout ticket en rapport avec votre matériel personnel (installation, erreur spécifique windows/mac, etc...) ne sera plus traitée et désormais supprimée.    
    Cordialement,
    L'équipe ACDC."""
    return embed


def rulesEmbedEn():
    """
    Create embed for rules of ticket
    @return: Embed
    """
    embed = discord.Embed(title="Ticket rules", color=discord.Color.yellow())
    embed.description = """Please respect the following rules:
     :one: Everything written in this channel is visible by the assistants, as well as the moderators of the server. If you want your question to be kept private, please do not ask it here.
     :two: Code sharing is prohibited, your screens must not contain code.
     :three: Look carefully if your question has not already been asked before asking it, otherwise it will be considered a duplicate.
     :four: Don't ping the assistants, they'll get back to you as soon as they can. Don't DM them unless they ask you to do so.
     :five: Specify your problem, and put an explicit title to your ticket, in case other people would ask the same question.
     :six: Tag your ticket with one or more tag(s) to make it easier for assistants and other students to find your question.
     :seven: All questions regarding tests won't be answered and will be deleted.
     :eight: Practicals are made to be done on the PIE (the school's machines). In this sense, any ticket related to your personal equipment (installation, specific windows/mac error, etc...) will no longer be answered and will now be deleted.

     Cordially,
     The ACDC team."""
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


def statusButton(status: TypeStatusTicket):
    """ Create button for status
    @param status: Status of the ticket
    @return: Button
    """
    label = ""
    style = discord.ButtonStyle.grey
    emoji = None
    match status:
        case TypeStatusTicket.Created:
            label = "Created"
            style = discord.ButtonStyle.green
            emoji = "🆕"
        case TypeStatusTicket.Recreated:
            label = "Recreated"
            style = discord.ButtonStyle.green
            emoji = "🆕"
        case TypeStatusTicket.Joined:
            label = "Joined"
            style = discord.ButtonStyle.green
            emoji = "✅"
        case TypeStatusTicket.Resolved:
            label = "Resolved"
            style = discord.ButtonStyle.grey
            emoji = "✅"
        case TypeStatusTicket.Duplicate:
            label = "Duplicate"
            style = discord.ButtonStyle.red
            emoji = "⚠️"
        case TypeStatusTicket.Closed:
            label = "Closed"
            style = discord.ButtonStyle.red
            emoji = "❌"

    return discord.ui.Button(label=label, style=style, emoji=emoji, disabled=True)


def reopenEmbed(thread: discord.Thread, manager: discord.Member):
    """
    Create embed for reopen thread
    @param thread: Thread
    @param manager: Member who reopen the thread
    @return: Embed
    """
    embed = discord.Embed(title="Your ticket has been closed", color=discord.Color.blue())
    embed.description = f"Your ticket {thread.name} has been closed by {manager.mention}. " \
                        f"If you want to reopen it, please click on the button below."
    embed.set_author(name=manager.display_name, icon_url=manager.display_avatar)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=f"Thread ID: {thread.parent.id} {thread.id}")
    return embed
