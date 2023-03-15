#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord
from discord.app_commands import Command


async def intra(interaction: discord.Interaction):
    await interaction.response.send_message("https://intra.forge.epita.fr/epita-prepa-acdc")


command = Command(name="intra", description="Get the intra link", callback=intra)
