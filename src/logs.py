#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

from uuid import UUID

import discord

from src.domain.entity.close_type import CloseType
from src.utils import setup_logging

_log = setup_logging(__name__)


def close_ticket(manager: discord.Member, type: CloseType, ticket_id: int, reason: str):
    """
    Logs a ticket closing
    @param manager: User who closed the ticket
    @param type: Type of closing (Resolve, Duplicate, Delete, ForceResolve, Other)
    @param ticket_id: ID of the ticket
    @param reason: Reason of the closing
    @return: None
    """
    _log.info(
        f'action=close_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} type={type.name} ticket_id={ticket_id} reason=\"{reason}\"')


def new_ticket(ticket_id: int, name: str, student: discord.Member):
    """
    Logs a new ticket creation
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param student: User who created the ticket
    @return: None
    """
    _log.info(
        f"action=new_ticket name=\"{name}\" user_id={student.id} user={student.name}#{student.discriminator} ticket_id={ticket_id}")


def renamed_ticket(user: discord.Member, ticket_id: int, old_name: str, name: str):
    """
    Logs a ticket renaming
    @param user: User who renamed the ticket
    @param ticket_id: ID of the ticket
    @param old_name: Old name of the ticket
    @param name: New name of the ticket
    @return: None
    """
    _log.info(
        f"action=renamed_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} old_name=\"{old_name}\" name=\"{name}\"")


def deleted_ticket(ticket_id: int, name: str, user: discord.Member):
    """
    Logs a ticket deletion
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param user: User who deleted the ticket
    @return:
    """
    _log.info(
        f"action=deleted_ticket ticket_id={ticket_id} name=\"{name}\" user_id={user.id} user={user.name}#{user.discriminator}")

def joined_ticket(manager: discord.Member, ticket_id: int):
    """
    Logs a ticket joining
    @param manager: User who joined the ticket
    @param ticket_id: ID of the ticket
    @return: None
    """
    _log.info(
        f"action=joined_ticket user_id={manager.id} user={manager.name}#{manager.discriminator} ticket_id={ticket_id}")


def error(user: discord.Member, err: Exception, id_err: UUID):
    """
    Logs an error
    @param user: User who caused the error
    @param err: Error
    @param id_err: ID of the error
    @return: None
    """
    _log.error(f"action=error user_id={user.id} user={user.name}#{user.discriminator} error={err} err_id={id_err}")
    _log.exception(err)


def reopen_ticket(user: discord.Member, ticket_id: int, name: str, owner: discord.Member):
    """
    Logs a ticket reopening
    @param user: User who reopened the ticket
    @param ticket_id: ID of the ticket
    @param name: Name of the ticket
    @param owner: Owner of the ticket
    @return: None
    """
    _log.info(
        f"action=reopen_ticket user_id={user.id} user={user.name}#{user.discriminator} ticket_id={ticket_id} name=\"{name}\" owner_id={owner.id} owner={owner.name}#{owner.discriminator}")


def trace_ticket(user: discord.Member, channel_id: int, login: str, tag: str):
    """
    Logs a ticket tracing
    @param user: User who traced the ticket
    @param channel_id: ID of the channel
    @param login: Login of the user
    @param tag: Tag of the user
    @return: None
    """
    _log.info(
        f"action=trace_ticket user_id={user.id} user={user.name}#{user.discriminator} channel_id={channel_id} login=\"{login}\" tag=\"{tag}\"")


def closed_trace_ticket(user: discord.Member, channel_id: int, tag: str):
    """
    Logs a ticket closing
    @param user: User who closed the ticket
    @param channel_id: ID of the channel
    @param tag: Tag of the ticket
    @return: None
    """
    _log.info(
        f"action=closed_trace_ticket user_id={user.id} user={user.name}#{user.discriminator} channel_id={channel_id} tag=\"{tag}\"")


def new_participant(author: discord.Member, ticket_id: int):
    _log.info(
        f"action=new_participant user_id={author.id} user={author.name}#{author.discriminator} ticket_id={ticket_id}")