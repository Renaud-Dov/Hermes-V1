#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from discord.app_commands import Command

from src.actions import links, tickets, extras

commands = [
    {'command': Command(name="google", description="What do you know about `Let me google that for you`?",
                        callback=links.google.google)},
    {'command': Command(name="intra", description="Get the intra link", callback=links.intra.intra)},
    {'command': Command(name="git", description="Get the git link", callback=links.git.git)},
    {'command': Command(name="close", description="Mark a ticket as resolved", callback=tickets.close)},
    {'command': Command(name="rename", description="Rename a ticket", callback=tickets.rename)},
    {'command': Command(name="link", description="Link to another ticket", callback=links.link.link)},
    {'command': Command(name="abel", description="...", callback=extras.send_message)},
]
