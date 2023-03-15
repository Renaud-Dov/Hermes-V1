#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import logging
from uuid import UUID

import discord

from src.db import execute_sql, cursor
from src.types import TypeClose

logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def close_ticket(manager: discord.Member, type: TypeClose, ticket_id: int, reason: str):
    """
    Logs a ticket closing
    @param manager: User who closed the ticket
    @param type: Type of closing (Resolve, Duplicate, Delete, ForceResolve, Other)
    @param ticket_id: ID of the ticket
    @param reason: Reason of the closing
    @return: None
    """
    logger.info(
        f'action=close_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} type={type.name} ticket_id={ticket_id} reason=\"{reason}\"')

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("closed", ticket_id, f"{manager.name}#{manager.discriminator}", reason))
    execute_sql()


def new_ticket(ticket_id: int, name: str, student: discord.Member):
    """
    Logs a new ticket creation
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param student: User who created the ticket
    @return: None
    """
    logger.info(
        f"action=new_ticket name=\"{name}\" user_id={student.id} user={student.name}#{student.discriminator} ticket_id={ticket_id}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("new", str(ticket_id), f"{student.name}#{student.discriminator}", name))
    execute_sql()


def renamed_ticket(user: discord.Member, ticket_id: int, old_name: str, name: str):
    """
    Logs a ticket renaming
    @param user: User who renamed the ticket
    @param ticket_id: ID of the ticket
    @param old_name: Old name of the ticket
    @param name: New name of the ticket
    @return: None
    """
    logger.info(
        f"action=renamed_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} old_name=\"{old_name}\" name=\"{name}\"")

    cursor.execute("INSERT INTO Logs (log_type,ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("renamed", str(ticket_id), f"{user.name}#{user.discriminator}",
                    f"Renamed ticket {ticket_id} from \"{old_name}\" to \"{name}\""))
    execute_sql()


def deleted_ticket(ticket_id: int, name: str, user: discord.Member):
    """
    Logs a ticket deletion
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param user: User who deleted the ticket
    @return:
    """
    logger.info(
        f"action=deleted_ticket ticket_id={ticket_id} name=\"{name}\" user_id={user.id} user={user.name}#{user.discriminator}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("deleted", str(ticket_id), f"{user.name}#{user.discriminator}", f"Deleted ticket {ticket_id}"))
    execute_sql()


def joined_ticket(manager: discord.Member, ticket_id: int):
    """
    Logs a ticket joining
    @param manager: User who joined the ticket
    @param ticket_id: ID of the ticket
    @return: None
    """
    logger.info(
        f"action=joined_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} ticket_id={ticket_id}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("joined", str(ticket_id), f"{manager.name}#{manager.discriminator}", f"Joined ticket {ticket_id}"))
    execute_sql()


def error(user: discord.Member, err: Exception, id_err: UUID):
    """
    Logs an error
    @param user: User who caused the error
    @param err: Error
    @param id_err: ID of the error
    @return: None
    """
    logger.error(f"action=error user_id={user.id} user={user.name}#{user.discriminator} error={err} err_id={id_err}")


def reopen_ticket(user: discord.Member, ticket_id: int, name: str, owner: discord.Member):
    """
    Logs a ticket reopening
    @param user: User who reopened the ticket
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param owner: Owner of the ticket
    @return: None
    """
    logger.info(
        f"action=reopen_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} name=\"{name}\" owner_id={owner.id} owner={owner.name}#{owner.discriminator}")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("reopened", str(ticket_id), f"{user.name}#{user.discriminator}", f"Reopened ticket {ticket_id}"))
    execute_sql()


def trace_ticket(user: discord.Member, channel_id: int, login: str, tag: str):
    """
    Logs a ticket tracing
    @param user: User who traced the ticket
    @param channel_id: ID of the channel
    @param login: Login of the user
    @param tag: Tag of the user
    @return: None
    """
    logger.info(
        f"action=trace_ticket user_id={user.id} user={user.name}#{user.discriminator} channel_id={channel_id} login=\"{login}\" tag=\"{tag}\"")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("trace", str(channel_id), f"{user.name}#{user.discriminator}", f"Tag [{tag}] Login [{login}]"))
    execute_sql()


def closed_trace_ticket(user: discord.Member, channel_id: int, tag: str):
    """
    Logs a ticket closing
    @param user: User who closed the ticket
    @param channel_id: ID of the channel
    @param tag: Tag of the user
    @return: None
    """
    logger.info(
        f"action=closed_trace_ticket user_id={user.id} user={user.name}#{user.discriminator} channel_id={channel_id} tag=\"{tag}\"")

    cursor.execute("INSERT INTO Logs (log_type, ticket_id, done_by, log_message) VALUES (%s, %s, %s, %s)",
                   ("closed_trace", str(channel_id), f"{user.name}#{user.discriminator}", f"Tag [{tag}]"))
    execute_sql()
