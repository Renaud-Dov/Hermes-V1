#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

from datetime import datetime
from typing import List, Optional, Dict

import discord
import yaml
import re


class ManagerFormat:
    def __init__(self, manager: dict):
        self.manager = manager
        self.category = manager["category"]
        self.ticket_msg = manager["ticket_msg"]
        self.roles: List[int] = manager["roles"] if "roles" in manager else []
        self.users: List[int] = manager["users"] if "users" in manager else []


class SettingsFormat:
    def __init__(self, managers: List[dict]):
        # regex for matching a discord snowflake
        self.managers = [ManagerFormat(m) for m in managers]


class PracticalsTagFormat:
    def __init__(self, tag: dict):
        self.id = tag["id"]
        self.from_date = datetime.strptime(tag["from"], "%Y-%m-%d %H:%M:%S")
        self.to_date = datetime.strptime(tag["to"], "%Y-%m-%d %H:%M:%S")

class ForumFormat:
    def __init__(self, forum: dict):
        self.id = forum["id"]
        self.end_tag = forum["end_tag"]
        self.webhook_channel = forum["webhook_channel"]
        self.practicals_tags = [PracticalsTagFormat(tag) for tag in forum["practicals_tags"]]


class TicketFormat:
    def __init__(self, ticket: dict):
        self.open_tag = ticket["open_tag"]
        self.webhook_channel = ticket["webhook_channel"]
        self.category_channel = ticket["category_channel"]
        self.groups: List[str] = ticket["groups"] if "groups" in ticket else []


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f)
        self.settings = SettingsFormat(**self._config['settings'])

        self.forums = [ForumFormat(list(forum.values())[0]) for forum in self._config['forums']]
        self.tickets = {key: TicketFormat(value) for key, value in self._config['tickets'].items()}
        self.groups: Dict[str, int] = self._config['groups']
        self.tags : List[int] = self._config['tags']

    def get_forum(self, forum_id):
        return next((forum for forum in self.forums if forum.id == forum_id), None)

    def get_open_tag_tickets(self):
        """Returns a list of open tickets categories"""
        return [ticket for ticket in self.tickets if self.tickets[ticket].open_tag]


    def __get_tickets_groupsIDS(self, ticket: TicketFormat) -> List[int]:
        """Returns a list of group ids for a ticket"""
        return [self.groups[group] for group in ticket.groups]

    def get_all_tickets_categories(self):
        """Returns a list of all tickets categories"""
        return [ticket.category_channel for ticket in self.tickets.values()]

    def got_ticket_group(self, ticket: TicketFormat, roles: List[int]):
        """Checks if the user has a role that is in the ticket groups"""
        tickets_groups = self.__get_tickets_groupsIDS(ticket)
        return any(role in tickets_groups for role in roles)


    def get_week_practical_tag(self, thread: discord.Thread):
        """Returns the tag of the week of the date"""
        now = datetime.now()
        a = thread.applied_tags
        b = [tag.id for tag in a if tag.id in self.tags]
        # if the thread has a tag that is in the config tags, skip it
        for tag_id in b:
            if tag_id in self.tags:
                return None
        forum = self.get_forum(thread.parent_id)
        if forum:
            for tag in forum.practicals_tags:
                if tag.from_date <= now <= tag.to_date:
                    return tag.id
        return None




