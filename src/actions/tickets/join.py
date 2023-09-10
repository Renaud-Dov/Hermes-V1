#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.client import HermesClient
from src.data.engine import engine
from src.data.models import Ticket, TicketParticipant
from src.other import Embed
from src.other.tools import find_ticket_from_logs


async def join_ticket(client: HermesClient, thread_member: discord.ThreadMember):
    thread = thread_member.thread
    config = client.get_config(thread.guild.id)
    member: discord.Member = thread_member.thread.guild.get_member(thread_member.id)
    config_forum = config.get_forum(thread.parent_id)

    if not config_forum or thread.archived:
        return
    category = config.get_manager_category(member)
    if not category:
        return
    log_chan = client.get_channel(config_forum.webhook_channel)
    message = await find_ticket_from_logs(log_chan, str(thread.id))


    session = Session(engine)
    ticket  = session.execute(select(Ticket).where(Ticket.thread_id == str(thread.id))).scalar_one_or_none()
    if not ticket:
        return

    # if user is already in the ticket participants, we don't add him again
    if next((p for p in ticket.participants if p.user_id == str(member.id)), None):
        return

    ticket.updated_at = datetime.utcnow()
    ticket.participants.append(TicketParticipant(user_id=member.id,taken_at=datetime.utcnow()))

    session.commit()

