#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import uuid

import discord
from discord.app_commands import AppCommandError

from src import exceptions
from src import logs


def get_error_message(error: AppCommandError) -> str:
    print(error, type(error))
    match type(error):
        case discord.errors.NotFound:
            return "The interaction was not found"
        case discord.errors.Forbidden:
            return "The bot does not have the permission to send messages to this user"
        case discord.errors.HTTPException:
            return "An HTTP error occurred"
        case discord.errors.InteractionResponded:
            return "The interaction has already been responded to"
        case discord.app_commands.CheckFailure:
            return "You are not allowed to use this command"
        case discord.app_commands.CommandInvokeError:
            return "An error occurred while invoking the command"
        case discord.app_commands.CommandNotFound:
            return "The command was not found"
        case exceptions.NotAThread:
            return "This is not a thread, you can't use this command here"
        case _:
            return "Unknown error"


async def errors(interaction: discord.Interaction, error: AppCommandError):
    message = get_error_message(error)
    id_err = uuid.uuid4()
    embed = discord.Embed(title="λάθος",
                          description=f"**An error occurred:** {message}.\n\nPlease try again later or contact an assistant.",
                          color=discord.Color.red())
    embed.add_field(name="ID Error", value=id_err, inline=False)
    embed.set_footer(text="μην τα σπας όλα")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.NotFound:  # interaction not found
        try:
            await interaction.user.send(embed=embed)
        except discord.errors.Forbidden:  # user blocked the bot
            pass
    except discord.errors.InteractionResponded:  # interaction already responded
        pass
    logs.error(interaction.user, error, id_err)
