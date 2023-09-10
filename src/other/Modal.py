#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import discord
from discord import ui

from src.domain.entity.guildConfig import TraceTag
from src.logs import trace_ticket
from src.other.Embed import newTraceEmbed, urlButton, rulesTicketEmbed
from src.other.tools import create_private_channel


class AskQuestion(ui.Modal, title='Trace ticket'):
    def __init__(self, category_tag: str, config_ticket: TraceTag):
        """
        Init the modal
        @param category_tag: Ticket category tag
        @param config_ticket: Ticket config
        """
        super().__init__()
        self.config_ticket = config_ticket
        self.category_tag = category_tag

    login = ui.TextInput(label='login (prenom.nom)')
    # tag = ui.TextInput(label='tag')
    question = ui.TextInput(label='Message (optional)', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        cat_channel = interaction.client.get_channel(self.config_ticket.category_channel)
        channel: discord.TextChannel = await create_private_channel(cat_channel, interaction.user,
                                                                    f"trace-{self.login.value}".replace(".", "_"))

        await interaction.response.send_message(f"Created channel {channel.mention}", ephemeral=True)

        await channel.send(embed=rulesTicketEmbed())
        msg = await channel.send(f"{interaction.user.mention} {self.login.value}")
        if self.question.value:
            await channel.send(self.question.value)

        view = discord.ui.View()
        view.add_item(urlButton(msg.jump_url))
        chan_logs = interaction.client.get_channel(self.config_ticket.webhook_channel)
        await chan_logs.send(
            embed=newTraceEmbed(interaction.user, self.category_tag, self.login.value, self.question.value, channel),
            view=view)
        trace_ticket(interaction.user, channel.id, self.login.value, self.category_tag)
