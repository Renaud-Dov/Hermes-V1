import logging

import discord

from src.types import TypeClose

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def format_user(user: discord.User or discord.Member):
    return f"({user.id},{user.name}#{user.discriminator})"


# ACTION="" ... etc

def close_ticket(manager: discord.Member, type: TypeClose, ticket_id: id, reason: str):
    logger.info(
        f'ACTION=close_ticket manager={format_user(manager)} type={type.name} ticket_id={ticket_id} reason=`{reason}`')


def new_ticket(category: str, student: discord.Member):
    logger.info(f"ACTION=new_ticket category={category} student={format_user(student)}")
