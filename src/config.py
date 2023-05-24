#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

from datetime import datetime
from typing import List, Optional, Dict
from jsonschema import validate

import discord
import yaml
import json

file = open("schema.json", 'r')
schema = json.load(file)
file.close()


class Meta:
    def __init__(self, meta: dict):
        self.name: str = meta["name"]
        self.description: str = meta["description"]
        self.guild_id: int = meta["guild_id"]


class ExtraCommand:
    def __init__(self, command: dict):
        self.name: str = command["name"]
        self.description: str = command["description"]
        self.message: Optional[str] = command.get("message", "")
        self.embeds: Optional[List[dict]] = command.get("embeds", [])
        self.embeds = [discord.Embed(title=embed["title"], description=embed["description"]) for embed in self.embeds]
        self.hidden: bool = command.get("hidden", False)


class ManagerFormat:
    def __init__(self, manager: dict):
        self.manager = manager
        self.category = manager["category"]
        self.msg = manager["message"]
        self.roles: List[int] = manager.get("roles", [])
        if not self.roles:
            self.roles = []
        self.users: List[int] = manager.get("users", [])
        if not self.users:
            self.users = []


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
        self.name = ticket["name"]
        self.from_date = datetime.strptime(ticket["from"], "%Y-%m-%d %H:%M:%S")
        self.to_date = datetime.strptime(ticket["to"], "%Y-%m-%d %H:%M:%S")
        self.webhook_channel = ticket["webhook_channel"]
        self.category_channel = ticket["category_channel"]
        self.groups: List[str] = ticket["groups"] if "groups" in ticket else []

    def __str__(self):
        return self.name


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f)
        validate(instance=self._config, schema=schema)

        self.file_name = config_file
        self.meta = Meta(self._config["meta"])
        self.managers = [ManagerFormat(m) for m in self._config['managers']]

        self.forums = [ForumFormat(list(forum.values())[0]) for forum in self._config['forums']]
        self.tickets = [TicketFormat(ticket) for ticket in self._config['tickets']]
        self.groups: Dict[str, int] = self._config['groups']
        self.tags: List[int] = self._config['tags']

        self.extra_commands = [ExtraCommand(command) for command in self._config['extra_commands']]

    def get_forum(self, forum_id):
        return next((forum for forum in self.forums if forum.id == forum_id), None)

    def get_ticket(self, tag):
        return next((ticket for ticket in self.tickets if ticket.name == tag), None)

    def get_open_tag_tickets(self):
        """Returns a list of open tickets categories"""
        now = datetime.now()
        print(now)
        for ticket in self.tickets:
            print("ticket", ticket.name, ticket.from_date, ticket.to_date, ticket.from_date <= now <= ticket.to_date)
        return [ticket for ticket in self.tickets if ticket.from_date <= now <= ticket.to_date]

    def __get_tickets_groupsIDS(self, ticket: TicketFormat) -> List[int]:
        """Returns a list of group ids for a ticket"""
        return [self.groups[group] for group in ticket.groups]

    def get_all_tickets_categories(self):
        """Returns a list of all tickets categories"""
        return [ticket.category_channel for ticket in self.tickets]

    def got_ticket_group(self, ticket: TicketFormat, roles: List[int]):
        """Checks if the user has a role that is in the ticket groups"""
        tickets_groups = self.__get_tickets_groupsIDS(ticket)
        return any(role in tickets_groups for role in roles)

    def get_week_practical_tag(self, thread: discord.Thread):
        """
        Returns the tag id of the week practicals
        @param thread: Thread to check
        @return: Tag id or None
        """
        tags: list[int] = [tag.id for tag in thread.applied_tags if tag.id in self.tags]
        if tags:
            return None
        forum = self.get_forum(thread.parent_id)
        now = datetime.now()
        return next((tag.id for tag in forum.practicals_tags if tag.from_date <= now <= tag.to_date), None)

    def find_manager_category(self, member: discord.Member) -> Optional[ManagerFormat]:
        """
        Finds the manager category of a member
        @param member: Discord member
        @return: Manager category or None
        """
        for managers_category in self.managers:
            if member.id in managers_category.users:  # type: int
                return managers_category
            for role in member.roles:  # type: discord.Role
                if role.id in managers_category.roles:  # type: int
                    return managers_category
        return None
