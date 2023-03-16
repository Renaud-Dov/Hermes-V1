#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord


async def intra(interaction: discord.Interaction):
    await interaction.response.send_message("https://intra.forge.epita.fr/epita-prepa-acdc")