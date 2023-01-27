import discord
from discord import ui
import random

from src.ConfigFormat import TicketFormat
from src.Embed import newTicketEmbed, urlButton, rulesTicketEmbed
from src.tools import create_private_channel


class AskQuestion(ui.Modal, title='Votre question'):
    def __init__(self, category_tag: str, config_ticket: TicketFormat):
        super().__init__()
        self.config_ticket = config_ticket
        self.category_tag = category_tag

    login = ui.TextInput(label='login')
    tag = ui.TextInput(label='tag')
    question = ui.TextInput(label='Message (optional)', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # channel: discord.TextChannel = await create_private_channel(
        # await channel.send(embed=rulesTicketEmbed())
        # msg = await channel.send(f"{interaction.user.mention} {self.login.value}")
        # await channel.send(self.question.value)
        log_chan = interaction.client.get_channel(1040188840557682740)
        # view = discord.ui.View()
        # view.add_item(urlButton(msg.jump_url))
        await log_chan.send(
            embed=newTicketEmbed(interaction.user, self.category_tag, self.login.value, self.question.value, self.tag.value))
        await interaction.response.send_message(f"Your trace has been reported to the team.")
