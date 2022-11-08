import yaml
import re


class SettingsFormat:
    def __init__(self, managers: list[int]):
        # regex for matching a discord snowflake
        self.managers = [int(re.match("^[0-9]+", str(m)).group(0)) for m in managers]


class ForumFormat:
    def __init__(self, forum: dict):
        self.id = forum["id"]
        self.end_tag = forum["end_tag"]
        self.webhook_channel = forum["webhook_channel"]


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f)
        self.settings = SettingsFormat(**self._config['settings'])

        self.forums = [ForumFormat(list(forum.values())[0]) for forum in self._config['forums']]

    def get_forum(self, forum_id):
        for forum in self.forums:
            if forum.id == forum_id:
                return forum
        return None
