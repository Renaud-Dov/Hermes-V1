#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import asyncio
import datetime

import discord
from sqlalchemy.orm import Session

from src import logs
from src.client import HermesClient
from src.data.engine import engine
from src.data.models import Ticket, TicketLog
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType
from src.other import Embed


async def create_ticket(client: HermesClient, thread: discord.Thread):
    config = client.get_config(thread.guild.id)
    config_forum = config.get_forum(thread.parent_id)
    if not config_forum: # if the forum is not configured we don't create a ticket
        return

    await thread.join()

    current_tags = [thread.parent.get_tag(tag.id) for tag in config_forum.get_current_tags()] # get current tags

    if current_tags:
        await thread.add_tags(*current_tags)
        await thread.send(f"Auto added tag(s): {', '.join([tag.name for tag in current_tags])}")
        if None in current_tags:
            await thread.send(f"Error: a tag was not found.")

    if config_forum.trace_tag in [tag.name for tag in thread.applied_tags]: # if the trace tag is present
        await asyncio.sleep(0.5) # avoid discord latency
        await thread.send("Merci de préciser votre login et le tag de votre trace ci dessous./Please specify your "
                          f"login and the tag of your trace below. {thread.owner.mention}")

    await thread.edit(auto_archive_duration=10080)  # 7 days to archive
    embed = Embed.newThreadEmbed(thread, Status.OPEN)
    view = discord.ui.View().add_item(Embed.urlButton(thread.jump_url))
    webhook = client.get_channel(config_forum.webhook_channel)
    webhook_msg = await webhook.send(embed=embed, view=view)
    time = datetime.datetime.utcnow()
    with Session(engine) as session: # create ticket in database
        ticket = Ticket(thread_id=thread.id, created_by=thread.owner_id,created_at=time, updated_at=time, name=thread.name, forum_id=thread.parent_id, guild_id=thread.guild.id,
                        webhook_message_url=webhook_msg.jump_url)
        session.add(ticket)

        log = TicketLog(ticket=ticket, kind=LogType.CREATED_TICKET, by=thread.owner_id,at=time)
        session.add(log)

        session.commit()
        thread = await thread.edit(name=f"[{ticket.id}] {thread.name}")
        logs.new_ticket(thread.id, thread.name, thread.owner)


