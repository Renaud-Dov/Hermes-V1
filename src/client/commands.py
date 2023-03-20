#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from discord.app_commands import Command

from src.actions import links, tickets, extras

commands = [
    {'command': Command(name="google", description="What do you know about `Let me google that for you`?",
                        callback=links.google)},
    {'command': Command(name="intra", description="Get the intra link", callback=links.intra)},
    {'command': Command(name="git", description="Get the git link", callback=links.git)},
    {'command': Command(name="close", description="Mark a ticket as resolved", callback=tickets.close)},
    {'command': Command(name="rename", description="Rename a ticket", callback=tickets.rename)},
    {'command': Command(name="link", description="Link to another ticket", callback=links.link)},
    {'command': Command(name="abel", description="...", callback=extras.send_message)},
    {'command': Command(name="trace", description="Trace a ticket", callback=tickets.trace_ticket)},
    {'command': Command(name="close_trace", description="Close a trace ticket", callback=tickets.close_trace_ticket)},
    {'command': Command(name="close_all", description="Close all tickets with a specific tag",
                        callback=tickets.close_all)},
]
