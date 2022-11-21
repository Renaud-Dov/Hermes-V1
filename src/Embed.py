import discord

from src import tools, actions
from src.ConfigFormat import Config
from src.types import TypeStatusTicket


def urlButton(url: str):
    return discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=url)


class ReopenView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = 3600

    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.green, emoji="🔓")
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await actions.reopen_ticket(interaction)


def strTag(tag: discord.ForumTag):
    s = f"**{tag.name}**"
    if tag.emoji:
        s += f" {tag.emoji}"
    return s


def newThreadEmbed(thread: discord.Thread, status: TypeStatusTicket):
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
        embed.add_field(name="Tags", value="\n".join([strTag(tag) for tag in thread.applied_tags]))

    embed.set_footer(text=f"Thread ID: {thread.id}")
    return embed


def doneEmbed(member: discord.Member, status: str, config: Config):
    embed = discord.Embed(title="Ticket has been closed by an assistant.", color=discord.Color.blue())
    category = tools.find_manager_category(member, config)
    if category:
        embed.title = category.ticket_msg

    if status == "Duplicate":
        embed.colour = discord.Colour.red()
        embed.title = "This question has already been answered. Please check if your question is already answered " \
                      "before creating a new ticket."

    embed.set_author(name=member.display_name, icon_url=member.display_avatar)  # TODO: change name to server name
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="If you have any further questions, please create a new ticket.")
    return embed


def editEmbed(embed: discord.Embed, member: discord.Member, status: TypeStatusTicket):
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

    for field in embed.fields:
        if field.name == "Action done by":
            embed.remove_field(embed.fields.index(field))
            break
    embed.add_field(name="Action done by", value=member.mention)

    embed.timestamp = discord.utils.utcnow()


def newTicketEmbed(student: discord.Member, category_tag: str, login: str, question: str, channel: discord.TextChannel):
    embed = discord.Embed(title="New ticket created", color=discord.Color.orange())
    embed.description = question
    embed.set_author(name=student.display_name, icon_url=student.display_avatar)
    embed.add_field(name="Login", value=login)
    embed.add_field(name="Tag Category", value=category_tag)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=f"Channel ID: {channel.id}")
    return embed


def rulesTicketEmbed():
    embed = discord.Embed(title="Règles relatives aux tickets privés", color=discord.Color.green())
    embed.description = """Tout ce qui est écrit dans ce channel est visible par les assistants, ainsi que les 
    modérateurs du serveur. Si vous souhaitez que votre question reste privée, merci de ne pas la poser ici.
    Le partage de code est autorisé, uniquement sur ce channel. Si vous souhaitez partager du code, merci de le mettre 
    dans un [code block](https://support.discord.com/hc/fr/articles/210298617) ou par fichier.
    
    Cordialement,
    L'équipe ACDC."""
    return embed


def rulesEmbed():
    embed = discord.Embed(title="Règles relatives aux tickets", color=discord.Color.yellow())
    embed.description = """Merci de respecter les règles suivantes :
    :one: Tout ce qui est écrit dans ce channel est visible par les assistants, ainsi que les modérateurs du serveur. Si vous souhaitez que votre question reste privée, merci de ne pas la poser ici.
    :two: Le partage de code est interdit, vos screens ne doivent pas contenir de code.
    :three: Regardez bien si votre question n'a pas déjà été posée avant de la poser, sinon elle sera considérée comme doublon.
    :four: Ne pas ping les assistants, ils vous répondront dès qu'ils le pourront.
    :five: Spécifiez bien votre problème, et mettez un titre explicite à votre ticket, au cas où d'autres personnes se poserait la même question.
    :six: Mettez un ou plusieurs tags à votre ticket, afin de faciliter la recherche de votre question par les assistants et les autres étudiants.
    
    Cordialement,
    L'équipe ACDC."""
    return embed


def deletedThreadEmbed(thread: discord.Thread):
    embed = discord.Embed(title="Ticket has been deleted", color=discord.Color.red())
    embed.description = f"Ticket {thread.name} has been deleted by {thread.owner.mention}"
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=f"Thread ID: {thread.id}")
    return embed


def statusButton(status: TypeStatusTicket):
    label = ""
    style = discord.ButtonStyle.grey
    emoji = ""
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
    embed = discord.Embed(title="Your ticket has been closed", color=discord.Color.blue())
    embed.description = f"Your ticket {thread.name} has been closed by {manager.mention}. " \
                        f"If you want to reopen it, please click on the button below."
    embed.set_author(name=manager.display_name, icon_url=manager.display_avatar)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=f"Thread ID: {thread.parent.id} {thread.id}")
    return embed
