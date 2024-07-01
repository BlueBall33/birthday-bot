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

from views import HelpView

def formatBytes(bytes: int, unit: bool = False):
    if bytes <= 1_000_000_000:
        return f"{bytes / (1024 ** 2):.1f}" + ("MB" if unit else "")

    else:
        return f"{bytes / (1024 ** 3):.1f}" + ("GB" if unit else "")

class Settings(commands.Cog, name="settings"):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.description = ""



    @commands.hybrid_group(
        name="settings",
        aliases=get_aliases("settings"),
        invoke_without_command=True
    )
    async def settings(self, ctx: commands.Context):
        view = HelpView(self.bot, ctx)
        embed = view.build_embed(self.qualified_name)
        view.response = await ctx.send(embed=embed, view=view)

    @settings.command(name="birthdayschanal", aliases=get_aliases("birthdaysChanal"))
    @commands.has_permissions(manage_guild=True)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def setbirthdayschanal(self, ctx: commands.Context, birthdayschanal:discord.TextChannel):
        "dsas"
        update_settings(ctx.guild.id, {"birthdaysChanal": birthdayschanal.id})
        await ctx.send(get_lang(ctx.guild.id, "setBirthdaysChanal").format(ctx.prefix, birthdayschanal))

    @settings.command(name="prefix", aliases=get_aliases("prefix"))
    @commands.has_permissions(manage_guild=True)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def prefix(self, ctx: commands.Context, prefix: str):
        "Change the default prefix for message commands."
        update_settings(ctx.guild.id, {"prefix": prefix})
        await ctx.send(get_lang(ctx.guild.id, "setPrefix").format(ctx.prefix, prefix))

    @settings.command(name="language", aliases=get_aliases("language"))
    @commands.has_permissions(manage_guild=True)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def language(self, ctx: commands.Context, language: str):
        "You can choose your preferred language, the bot message will change to the language you set."
        language = language.upper()
        if language not in LANGS:
            return await ctx.send(get_lang(ctx.guild.id, "languageNotFound"))

        update_settings(ctx.guild.id, {'langs': language})
        await ctx.send(get_lang(ctx.guild.id, 'changedLanguage').format(language))

    @language.autocomplete('language')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str) -> list:
        if current:
            return [app_commands.Choice(name=lang, value=lang) for lang in LANGS.keys() if current.upper() in lang]
        return [app_commands.Choice(name=lang, value=lang) for lang in LANGS.keys()]



    @settings.command(name="view", aliases=get_aliases("view"))
    @commands.has_permissions(manage_guild=True)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def view(self, ctx: commands.Context):
        "Show all the bot settings in your server."
        settings = get_settings(ctx.guild.id)
        embed = discord.Embed(color=sett.embed_color)
        embed.set_author(name=get_lang(ctx.guild.id, 'settingsMenu').format(ctx.guild.name), icon_url=self.bot.user.display_avatar.url)
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.add_field(name=get_lang(ctx.guild.id, 'settingsTitle'), value=get_lang(ctx.guild.id, 'settingsValue').format(
            settings.get('prefix', func.settings.bot_prefix) or "None",
            settings.get('langs', 'PL'),
            inline=True)
        )
        embed.add_field(name=get_lang(ctx.guild.id, 'settingsTitleBr'), value=get_lang(ctx.guild.id, 'settingsValueBr').format(
            f"<#{settings.get('birthdaysChanal')}>" or "None",
            inline=False)
        )

        perms = ctx.guild.me.guild_permissions
        embed.add_field(name=get_lang(ctx.guild.id, 'settingsPermTitle'), value=get_lang(ctx.guild.id, 'settingsPermValue').format(
            '<a:Check:1245829058877591703>' if perms.administrator else '<a:Cross:1245829056164003941>',
            '<a:Check:1245829058877591703>' if perms.manage_guild else '<a:Cross:1245829056164003941>',
            '<a:Check:1245829058877591703>' if perms.manage_channels else '<a:Cross:1245829056164003941>',
            '<a:Check:1245829058877591703>' if perms.manage_messages else '<a:Cross:1245829056164003941>'), inline=False
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))