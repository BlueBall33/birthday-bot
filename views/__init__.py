from discord.ext import commands


class ButtonOnCooldown(commands.CommandError):
    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after


from .help import HelpView
from .link import LinkView