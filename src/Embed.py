import discord

from src.ConfigFormat import Config


def urlButton(url: str):
    return discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=url)


class newThreadView(discord.ui.View):
    def __init__(self, url: str):
        super().__init__(timeout=None)
        self.add_item(urlButton(url))

    @discord.ui.button(label="Resolve ticket", style=discord.ButtonStyle.green, emoji="✅")
    async def resolve(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed: discord.Embed = interaction.message.embeds[0]
        editEmbed(embed, interaction.user, "Resolved")

        id_thread = int(interaction.message.embeds[0].footer.text.lstrip("Thread ID:"))
        embed.timestamp = discord.utils.utcnow()

        thread: discord.Thread = interaction.client.get_channel(id_thread)
        if thread is None:
            await interaction.response.send_message("Thread not found", ephemeral=True)
            return
        forum: discord.ForumChannel = thread.parent
        config = Config("config.yaml")
        config_forum = config.get_forum(forum.id)
        if not config_forum:
            await interaction.response.send_message("Forum not found", ephemeral=True)
            return
        for tag in forum.available_tags:
            if tag.name == config_forum.end_tag:
                await thread.add_tags(tag)
                break

        await thread.send(embed=doneEmbed(interaction.user, "Resolved", ""))

        view = discord.ui.View()
        view.add_item(urlButton(thread.jump_url))
        await interaction.response.send_message("Marked as done", ephemeral=True)
        await interaction.message.edit(embed=embed, view=view)


def strTag(tag: discord.ForumTag):
    s = f"**{tag.name}**"
    if tag.emoji:
        s += f" {tag.emoji}"
    return s


def newThreadEmbed(thread: discord.Thread):
    embed = discord.Embed(title=thread.name, color=discord.Color.orange())
    if thread.starter_message:
        embed.description = thread.starter_message.content
    embed.timestamp = thread.created_at
    embed.add_field(name="Status", value="Open 🟢")  # must be fist field
    embed.set_author(name=thread.owner.display_name, icon_url=thread.owner.display_avatar)
    if thread.applied_tags:
        embed.add_field(name="Tags", value="\n".join([strTag(tag) for tag in thread.applied_tags]))

    embed.set_footer(text=f"Thread ID: {thread.id}")
    return embed


def doneEmbed(member: discord.Member, status: str, reason: str = "Resolved"):
    embed = discord.Embed(title="Ticket has been closed by an assistant", color=discord.Color.blue())
    if reason:
        embed.description = reason
    if status == "Duplicate":
        embed.colour = discord.Colour.red()
        embed.title = "This question has already been answered. Please check if your question is already answered " \
                      "before creating a new thread."

    embed.set_author(name=member.display_name, icon_url=member.display_avatar)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="If you have any further questions, please create a new thread.")
    return embed


def editEmbed(embed: discord.Embed, member: discord.Member, status: str):
    if status == "Resolved":
        embed.set_field_at(0, name="Status", value="Done ✅")
        embed.colour = discord.Colour.light_gray()
    elif status == "Duplicate":
        embed.set_field_at(0, name="Status", value="Duplicate 🟡")
        embed.colour = discord.Colour.gold()
    elif status == "Closed":
        embed.set_field_at(0, name="Status", value="Closed 🔴")
        embed.colour = discord.Colour.red()
    elif status == "Joined":
        embed.set_field_at(0, name="Status", value="Joined 🟢")
        embed.colour = discord.Colour.orange()
    embed.add_field(name="Action done by", value=member.mention)

    embed.timestamp = discord.utils.utcnow()
