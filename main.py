import os
import sys
import traceback
import aiohttp
import funcion as func
import discord
from discord.ext import commands

func.init()


class Translator(discord.app_commands.Translator):
    async def load(self):
        print("Loaded Translator")

    async def unload(self):
        print("Unload Translator")

    async def translate(self, string: discord.app_commands.locale_str, locale: discord.Locale, context: discord.app_commands.TranslationContext):
        if str(locale) in func.LOCAL_LANGS:
            return func.LOCAL_LANGS[str(locale)].get(string.message, None)
        return None

class BirthdayBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




    async def setup_hook(self):
        func.langs_setup()
        for module in os.listdir(func.ROOT_DIR + '/cogs'):
            if module.endswith('.py'):
                try:
                    await self.load_extension(f"cogs.{module[:-3]}")
                    print(f"Loaded {module[:-3]}")
                except Exception as e:
                    print(traceback.format_exc())

        await self.tree.set_translator(Translator())
        await self.tree.sync()

    async def on_ready(self):
        print("------------------")
        print(f"Logging As {self.user}")
        print(f"Bot ID: {self.user.id}")
        print("------------------")
        print(f"Discord Version: {discord.__version__}")
        print(f"Python Version: {sys.version}")
        print("------------------")

        func.tokens.client_id = self.user.id
        func.LOCAL_LANGS.clear()

    async def on_command_error(self, ctx: commands.Context, exception, /) -> None:
        error = getattr(exception, 'original', exception)
        if ctx.interaction:
            error = getattr(error, 'original', error)
        if isinstance(error, (commands.CommandNotFound, aiohttp.client_exceptions.ClientOSError)):
            return

        elif isinstance(error, (
        commands.CommandOnCooldown, commands.MissingPermissions, commands.RangeError, commands.BadArgument)):
            pass

        elif isinstance(error, (commands.MissingRequiredArgument, commands.MissingRequiredAttachment)):
            command = f"{ctx.prefix}" + (
                f"{ctx.command.parent.qualified_name} " if ctx.command.parent else "") + f"{ctx.command.name} {ctx.command.signature}"
            position = command.find(f"<{ctx.current_parameter.name}>") + 1
            description = f"**Correct Usage:**\n```{command}\n" + " " * position + "^" * len(
                ctx.current_parameter.name) + "```\n"
            if ctx.command.aliases:
                description += f"**Aliases:**\n`{', '.join([f'{ctx.prefix}{alias}' for alias in ctx.command.aliases])}`\n\n"
            description += f"**Description:**\n{ctx.command.help}\n\u200b"

            embed = discord.Embed(description=description, color=func.settings.embed_color)
            embed.set_footer(icon_url=ctx.me.display_avatar.url, text=f"More Help: {func.settings.invite_link}")
            return await ctx.reply(embed=embed)

        try:
            return await ctx.reply(error, ephemeral=True)
        except:
            pass


async def get_prefix(bot, message: discord.Message):
    settings = func.get_settings(message.guild.id)
    return settings.get("prefix", func.settings.bot_prefix)

intents = discord.Intents.default()
intents.message_content = True if func.settings.bot_prefix else False
member_cache = discord.MemberCacheFlags(
    voice=True,
    joined=False
)

bot = BirthdayBot(
    command_prefix=get_prefix,
    help_command=None,
    chunk_guilds_at_startup=False,
    member_cache_flags=member_cache,
    activity=discord.Activity(type=discord.ActivityType.listening, name="Starting..."),
    case_insensitive=True,
    intents=intents
)

if __name__ == "__main__":
    bot.run(func.tokens.token, log_handler=None)