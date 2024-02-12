import discord
import random

from src.utils import setup_logging

messages = [
    ":tickets:",
    "🎫❓👀",
    "Hey ! Ça te dirait pas de faire un ticket ?",
    "Looks likes a ticket to me.",
    "Ça sens le ticket, tu devrais en faire un je pense :eyes:",
    "Opening a ticket is free of charge!"
]

_log = setup_logging(__name__)


async def fe1tike(interaction: discord.Interaction):
    await  interaction.response.send_message("done", ephemeral=True)
    message = random.choice(messages)
    _log.info(f"Command fe1tike called by {interaction.user.id} ({interaction.user.name}) in {interaction.guild_id}")

    await interaction.channel.send(message)




