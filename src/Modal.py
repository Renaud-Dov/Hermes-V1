import discord
from discord import ui
import random

from src.ConfigFormat import TicketFormat
from src.tickets import create_private_channel


class AskQuestion(ui.Modal, title='Votre question'):
    def __init__(self, config_ticket: TicketFormat):
        super().__init__()
        self.config_ticket = config_ticket

    login = ui.TextInput(label='login')
    question = ui.TextInput(label='Question', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel: discord.TextChannel = await create_private_channel(interaction.client.get_channel(self.config_ticket.category_channel),
                                     interaction.user, "ticket-{0}".format(random.randint(1, 9999)))
        msg = await channel.send(f"{interaction.user.mention} {self.login.value}")
        await channel.send(self.question.value)
        log_chan = interaction.client.get_channel(self.config_ticket.webhook_channel)
        await log_chan.send("New question from {0} ({1})".format(interaction.user.name, msg.jump_url))



