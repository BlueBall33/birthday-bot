import discord
import funcion as func
import psutil

from discord import app_commands
from discord.ext import commands
from funcion import (get_aliases,
                    get_settings,
                     cooldown_check,
                     update_settings,
                     LANGS,
                     get_lang,
                     settings as sett,)


class Birthday(commands.Cog, name="birthday"):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.description = ""


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Birthday(bot))