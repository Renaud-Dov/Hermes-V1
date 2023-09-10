#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
import re
from datetime import datetime

import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import logs
from src.client.checks import is_thread
from src.data.engine import engine
from src.data.models import Ticket, TicketLog
from src.domain.entity.logType import LogType
from src.utils import setup_logging

_log = setup_logging(__name__)


@is_thread()
async def rename(interaction: discord.Interaction, name: str):
    thread: discord.Thread = interaction.channel
    old_name = thread.name

    session = Session(engine)
    ticket = session.execute(select(Ticket).where(Ticket.thread_id == str(thread.id))).scalar_one_or_none()
    if not ticket:
        await interaction.response.send_message("This thread is not linked to a ticket!", ephemeral=True)
        return

    # keep [#NUMBER] at the beginning of the name
    name = f"[{ticket.id}] {name}"
    await thread.edit(name=name)
    await interaction.response.send_message(f"Renamed from `{old_name}` to `{name}`", ephemeral=True)
    logs.renamed_ticket(interaction.user, thread.id, old_name, name)
    ticket.updated_at = datetime.utcnow()
    log = TicketLog(ticket=ticket, kind=LogType.RENAMED_TICKET, by=interaction.user.id, message=f"Renamed from `{old_name}` to `{name}`",at=datetime.utcnow())
    session.add(log)
    session.commit()
