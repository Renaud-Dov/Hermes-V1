#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from discord.app_commands import Command

from src.actions import links, tickets, extras

commands = [
    {'command': Command(name="google", description="What do you know about `Let me google that for you`?",
                        callback=links.google)},
    {'command': Command(name="close", description="Mark a ticket as resolved", callback=tickets.close)},
    {'command': Command(name="rename", description="Rename a ticket", callback=tickets.rename)},
    # command to ask ticket creator to give explicit title to his ticket
    {'command': Command(name="ask_title", description="Ask ticket creator to give explicit title to his ticket",
                        callback=tickets.ask_title)},
    {'command': Command(name="link", description="Link to another ticket", callback=links.link)},
    {'command': Command(name="impersonate", description="...", callback=extras.send_message)},
    {'command': Command(name="trace", description="Trace a ticket", callback=tickets.trace_ticket)},
    {'command': Command(name="close_trace", description="Close a trace ticket", callback=tickets.close_trace_ticket)},
    # {'command': Command(name="close_all", description="Close all tickets with a specific tag",
    #                     callback=tickets.close_all)},
]
