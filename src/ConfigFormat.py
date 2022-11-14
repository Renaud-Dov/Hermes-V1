from typing import List, Optional

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


class ForumFormat:
    def __init__(self, forum: dict):
        self.id = forum["id"]
        self.end_tag = forum["end_tag"]
        self.webhook_channel = forum["webhook_channel"]


class TicketFormat:
    def __init__(self, ticket: dict):
        self.open_tag = ticket["open_tag"]
        self.webhook_channel = ticket["webhook_channel"]
        self.category_channel = ticket["category_channel"]


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f)
        self.settings = SettingsFormat(**self._config['settings'])

        self.forums = [ForumFormat(list(forum.values())[0]) for forum in self._config['forums']]
        self.tickets = {key: TicketFormat(value) for key, value in self._config['tickets'].items()}

    def get_forum(self, forum_id):
        for forum in self.forums:
            if forum.id == forum_id:
                return forum
        return None

    def get_open_tag_tickets(self):
        """Returns a list of open tickets categories"""
        open_tickets = []
        for ticket in self.tickets:
            if self.tickets[ticket].open_tag:
                open_tickets.append(ticket)
        return open_tickets

    def get_all_tickets_categories(self):
        """Returns a list of all tickets categories"""
        return [ticket.category_channel for ticket in self.tickets.values()]
