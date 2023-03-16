#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved
from discord.app_commands import AppCommandError


class NotAThread(AppCommandError):
    def __init__(self, message: str = "This is not a thread!"):
        super().__init__(message)
