#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import uuid

import discord
from discord.app_commands import AppCommandError

from src import logs


async def errors(interaction: discord.Interaction, error: AppCommandError):
    id_err = uuid.uuid4()
    embed = discord.Embed(title="λάθος",
                          description="An error occurred. Please try again later or contact an assistant",
                          color=discord.Color.red())
    embed.add_field(name="ID Error", value=id_err, inline=False)
    embed.set_footer(text="μην τα σπας όλα")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.NotFound:
        try:
            await interaction.user.send(embed=embed)
        except discord.errors.Forbidden:
            pass
    except discord.errors.InteractionResponded:
        pass
    logs.error(interaction.user, error, id_err)
