import datetime
import json
from typing import Optional, List

import yaml
from pydantic import BaseModel, Field, validator, field_validator, root_validator, model_validator


class Meta(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, description="Slug of the config")
    name: str = Field(..., min_length=1, max_length=100, description="Pretty name of the config")
    guild_id: int = Field(..., description="Guild ID where the students are")

class Manager(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, description="Slug of the manager")
    message: str = Field(..., description="Message when manager closes a ticket")
    roles: Optional[List[int]] = Field([], description="List of roles that can use the manager")
    users: Optional[List[int]] = Field([], description="List of users that can use the manager")

class PracticalTag(BaseModel):
    id: int = Field(..., description="ID of the practical tag")
    from_date: datetime.datetime = Field(..., description="From date of the practicals tag")
    to_date: datetime.datetime = Field(..., description="To date of the practicals tag")
class Forum(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, description="Slug of the forum")
    id: int = Field(..., description="ID of the forum")
    closing_tag: str = Field(..., description="Closing tag of the forum")
    trace_tag: str = Field(..., description="Trace tag of the forum")
    webhook_channel: int = Field(..., description="Webhook channel to repost the messages")
    practicals_tags: Optional[List[PracticalTag]] = Field([], description="List of practicals tags")


class Allowed(BaseModel):
    roles: Optional[List[int]] = Field([], description="List of roles that can use the trace")
    users: Optional[List[int]] = Field([], description="List of users that can use the trace")

class TraceTag(BaseModel):
    tag: str = Field(..., description="Tag category of the trace")
    from_date: datetime.datetime = Field(..., description="Date from when the tag is available")
    to_date: datetime.datetime = Field(..., description="Date to when the tag is available")
    category_channel: int = Field(..., description="Category channel where the trace must be created")
    webhook_channel: int = Field(..., description="Webhook channel to repost the messages")

    managers: List[Manager] = Field([], description="List of managers that can close the trace")
    allowed: Allowed = Field(..., description="Allowed roles/users to create a trace using this tag")

class Embed(BaseModel):
    title: str = Field(..., description="Title of the embed")
    description: str = Field(..., description="Description of the embed")
    color: Optional[int] = Field(None, description="Color of the embed")
class ExtraCommand(BaseModel):
    name: str = Field(..., description="Name of the command")
    description: str = Field(..., description="Description of the command")
    message: Optional[str] = Field("", description="Message of the command")
    embeds: Optional[List[Embed]] = Field([], description="List of embeds of the command")
    hide_command_response: bool = Field(False, description="Respond command in ephemeral message and send message in public")


class Config(BaseModel):
    meta: Meta = Field(..., description="Meta information about the config")
    managers: List[Manager] = Field(..., description="List of managers")
    forums: List[Forum] = Field(..., description="List of forums")
    trace_tags: List[TraceTag] = Field(..., description="List of trace tags")
    extra_commands: Optional[List[ExtraCommand]] = Field([], description="List of extra commands")

    def get_forum(self, forum_id: int) -> Optional[Forum]:
        return next((forum for forum in self.forums if forum.id == forum_id), None)

    def get_trace_tag(self, tag: str) -> Optional[TraceTag]:
        return next((trace_tag for trace_tag in self.trace_tags if trace_tag.tag == tag), None)



    def get_manager(self, manager_slug: str) -> Optional[Manager]:
        return next((manager for manager in self.managers if manager.slug == manager_slug), None)


file= "config/2027.yaml"
with open(file, 'r') as file:
    data = yaml.safe_load(file)

schema = Config.model_json_schema()
print(json.dumps(schema))
my_instance = Config(**data)


if __name__ == '__main__':
    print(my_instance)