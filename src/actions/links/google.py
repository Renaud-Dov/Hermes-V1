#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import json
import os
import urllib
from typing import Optional

import discord
import requests
from discord import app_commands

from src.utils import setup_logging

BITLY_TOKEN = os.getenv("BITLY_TOKEN")

_log = setup_logging(__name__)

# @tree.command(name="google", description="What do you know about `Let me google that for you`?")
@app_commands.describe(query="Query to search")
async def google(interaction: discord.Interaction, query: str, message: Optional[str]):
    """

    @param interaction:
    @param query: Query to search on google
    @param message: Message to send before the link
    @return:
    """
    # transform query in url format
    query = urllib.parse.quote(query)

    r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers={
        "Authorization": f"Bearer {BITLY_TOKEN}"
    }, data=json.dumps({
        "long_url": f"https://letmegooglethat.com/?q={query}"
    }))
    if not r.ok:
        await interaction.response.send_message(f"Error while creating link: {r.json()}", ephemeral=True)
        _log.error(f"Error while creating link: {r.json()}")
        return
    r = r.json()

    if message is None:
        message = ""
    else:
        message += " "
    await interaction.response.send_message("Send message", ephemeral=True)
    await interaction.channel.send(message + r["link"], suppress_embeds=True)

    _log.info(f"Google command used by {interaction.user} with query {query} : {r['link']}")
