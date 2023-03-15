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

from src.logs import logger

BITLY_TOKEN = os.getenv("BITLY_TOKEN")


# @tree.command(name="google", description="What do you know about `Let me google that for you`?")
@app_commands.describe(query="Query to search")
async def google(interaction: discord.Interaction, query: str, message: Optional[str]):
    # transform query in url format
    query = urllib.parse.quote(query)

    r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers={
        "Authorization": f"Bearer {BITLY_TOKEN}"
    }, data=json.dumps({
        "long_url": f"https://letmegooglethat.com/?q={query}"
    }))
    if not r.ok:
        await interaction.response.send_message(f"Error while creating link: {r.json()}", ephemeral=True)
        return
    r = r.json()

    if message is None:
        message = ""
    else:
        message += " "
    await interaction.response.send_message("Send message", ephemeral=True)
    await interaction.channel.send(message + r["link"], suppress_embeds=True)

    logger.info(f"Google command used by {interaction.user} with query {query} : {r['link']}")
