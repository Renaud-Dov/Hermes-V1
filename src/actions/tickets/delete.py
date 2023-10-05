#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import logs
from src.client import checks, HermesClient
from src.data.engine import engine
from src.data.models import TicketLog, Ticket
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType
from src.other import Embed


@checks.is_thread()
async def delete_ticket(client: HermesClient, thread: discord.Thread):
    config_forum = client.get_config(thread.guild.id).get_forum(thread.parent_id)
    if not config_forum:
        return
    embed = Embed.deletedThreadEmbed(thread)
    channel_id = config_forum.webhook_channel
    channel = client.get_channel(channel_id)
    await channel.send(embed=embed)


    logs.deleted_ticket(thread.id, thread.name, thread.owner)

    session = Session(engine)
    ticket = session.execute(select(Ticket).where(Ticket.thread_id == str(thread.id))).scalar_one_or_none()
    ticket.deleted_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    ticket.status = Status.DELETED

    log = TicketLog(ticket=ticket, kind=LogType.DELETED_TICKET, by="", message='', at=datetime.utcnow())
    session.add(log)
    session.commit()
