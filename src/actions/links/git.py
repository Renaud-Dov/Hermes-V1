#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import discord


async def git(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://prepa.pages.epita.fr/programming/students/2027/html/epita-git-tutorial.html")
