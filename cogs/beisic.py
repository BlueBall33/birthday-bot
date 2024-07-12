import discord
from discord import app_commands
from discord.ext import commands
from funcion import (
    get_lang,
    settings,
    cooldown_check,
    get_aliases
)


from views import HelpView

class Basic(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.description = ""


    async def help_autocomplete(self, interaction: discord.Interaction, current: str) -> list:
        return [app_commands.Choice(name=c.capitalize(), value=c) for c in self.bot.cogs if
                c not in ["Nodes", "Task"] and current in c]

    @commands.hybrid_command(name="help", aliases=get_aliases("help"))
    @app_commands.autocomplete(category=help_autocomplete)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def help(self, ctx: commands.Context, category: str = "News") -> None:
        "Lists all the commands."
        if category not in self.bot.cogs:
            category = "News"
        view = HelpView(self.bot, ctx)
        embed = view.build_embed(category)
        view.response = await ctx.send(embed=embed, view=view)


    @commands.hybrid_command(name="ping", aliases=get_aliases("ping"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def ping(self, ctx: commands.Context):
        "Test if the bot is alive, and see the delay between your commands and my response."
        embed = discord.Embed(color=settings.embed_color)
        embed.add_field(name=get_lang(ctx.guild.id, 'pingTitle1'), value=get_lang(ctx.guild.id, 'pingfield1').format(
            "0", "0", self.bot.latency, '😭' if self.bot.latency > 5 else ('😨' if self.bot.latency > 1 else '👌')))
        await ctx.send(embed=embed)




async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Basic(bot))