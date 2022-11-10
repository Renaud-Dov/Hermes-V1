import discord
from discord import ui
import random

from src.ConfigFormat import TicketFormat
from src.Embed import newTicketEmbed, urlButton, rulesEmbed
from src.tickets import create_private_channel


class AskQuestion(ui.Modal, title='Votre question'):
    def __init__(self, category_tag: str, config_ticket: TicketFormat):
        super().__init__()
        self.config_ticket = config_ticket
        self.category_tag = category_tag

    login = ui.TextInput(label='login')
    question = ui.TextInput(label='Question', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel: discord.TextChannel = await create_private_channel(
            interaction.client.get_channel(self.config_ticket.category_channel),
            interaction.user, f"ticket-{self.category_tag}-{random.randint(1, 9999)}")
        await channel.send(embed=rulesEmbed())
        msg = await channel.send(f"{interaction.user.mention} {self.login.value}")
        await channel.send(self.question.value)
        log_chan = interaction.client.get_channel(self.config_ticket.webhook_channel)
        view = discord.ui.View()
        view.add_item(urlButton(msg.jump_url))
        await log_chan.send(
            embed=newTicketEmbed(interaction.user, self.category_tag, self.login.value, self.question.value, channel),
            view=view)
        await interaction.response.send_message(f"A new ticket channel has been created in {channel.mention}",
                                                ephemeral=True)
