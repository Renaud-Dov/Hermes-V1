from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import logs
from src.client import HermesClient
from src.data.engine import engine
from src.data.models import Ticket, TicketParticipant, TicketLog
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType


async def on_message(client: HermesClient, message: discord.Message):
    if not message.channel or message.channel.type != discord.ChannelType.public_thread or  message.channel.locked:
        return

    thread: discord.Thread = message.channel

    config = client.get_config(message.guild.id)
    forum = config.get_forum(thread.parent_id)
    if not forum:
        return

    session = Session(engine)
    ticket = session.execute(select(Ticket).where(Ticket.thread_id == str(thread.id))).scalar_one_or_none()
    if not ticket or ticket.status == Status.CLOSED:
        return # if the thread is not linked to a ticket, we don't do anything

    if not config.get_manager_category(message.author): # if the user is not a manager, we don't do anything
        return

    # if user is already in the ticket participants, we don't add him again
    if next((p for p in ticket.participants if p.user_id == str(message.author.id)), None):
        return

    ticket.updated_at = datetime.utcnow()
    ticket.participants.append(TicketParticipant(user_id=message.author.id, taken_at=datetime.utcnow()))
    if ticket.status == Status.OPEN:
        ticket.taken_at = datetime.utcnow()
        ticket.status = Status.IN_PROGRESS

    log = TicketLog(ticket=ticket, kind=LogType.NEW_PARTICIPANT, by=message.author.id, at=datetime.utcnow())
    session.add(log)

    session.commit()
    logs.new_participant(message.author, thread.id)

