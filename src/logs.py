import logging
from os import environ
from uuid import UUID

import discord
import psycopg2

from src.types import TypeClose

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

conn = psycopg2.connect(
    host=environ.get("DB_HOST"),
    database=environ.get("DB_DATABASE"),
    user=environ.get("DB_USERNAME"),
    password=environ.get("DB_PASSWORD")
)

cursor = conn.cursor()


def close_ticket(manager: discord.Member, type: TypeClose, ticket_id: int, reason: str):
    logger.info(
        f'action=close_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} type={type.name} ticket_id={ticket_id} reason=\"{reason}\"')

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                     ("closed", ticket_id, f"{manager.name}#{manager.discriminator}", reason))

def new_ticket(ticket_id: int, name: str, student: discord.Member):
    logger.info(
        f"action=new_ticket name=\"{name}\" user_id={student.id} user={student.name}#{student.discriminator} ticket_id={ticket_id}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                        ("new", ticket_id, f"{student.name}#{student.discriminator}", name))


def renamed_ticket(user: discord.Member, ticket_id: int, old_name: str, name: str):
    logger.info(
        f"action=renamed_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} old_name=\"{old_name}\" name=\"{name}\"")

    cursor.execute("INSERT INTO Logs (log_type,ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("renamed", ticket_id, f"{user.name}#{user.discriminator}",
                    f"Renamed ticket {ticket_id} from \"{old_name}\" to \"{name}\""))


def deleted_ticket(ticket_id: int, name: str, user: discord.Member):
    logger.info(
        f"action=deleted_ticket ticket_id={ticket_id} name=\"{name}\" user_id={user.id} user={user.name}#{user.discriminator}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                     ("deleted", ticket_id, f"{user.name}#{user.discriminator}", f"Deleted ticket {ticket_id}"))


def joined_ticket(manager: discord.Member, ticket_id: int):
    logger.info(
        f"action=joined_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} ticket_id={ticket_id}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                     ("joined", ticket_id, f"{manager.name}#{manager.discriminator}", f"Joined ticket {ticket_id}"))


def error(user: discord.Member, err: Exception, id_err: UUID):
    logger.error(f"action=error user_id={user.id} user={user.name}#{user.discriminator} error={err} err_id={id_err}")


def reopen_ticket(user: discord.Member, ticket_id: int, name: str, owner: discord.Member):
    logger.info(
        f"action=reopen_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} name=\"{name}\" owner_id={owner.id} owner={owner.name}#{owner.discriminator}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                        ("reopened", ticket_id, f"{user.name}#{user.discriminator}", f"Reopened ticket {ticket_id}"))
