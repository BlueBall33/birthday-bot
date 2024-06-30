import discord
import funcion as func
import psutil
from datetime import datetime, date
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from funcion import (get_aliases,
                     get_settings,
                     cooldown_check,
                     update_settings,
                     update_user,
                     LANGS,
                     get_lang,
                     settings as sett,
                     get_user)

from views import HelpView


def date_month(day: int, month: int) -> bool:
    if month == 1 or 3 or 5 or 7 or 8 or 10 or 12:
        if not 0< day <= 31 :
            return False
    elif month == 2:
        if not 0< day <= 28:
            return False
    elif month == 4 or 6 or 9 or 11:
        if not 0< day <= 30:
            return False
    else:
        return True

class Birthday(commands.Cog, name="birthday"):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.description = ""


    @commands.hybrid_group(
        name="birthdays",
        aliases=get_aliases("birthday"),
        invoke_without_command=True
    )
    async def birthdays(self, ctx: commands.Context):
        view = HelpView(self.bot, ctx)
        embed = view.build_embed(self.qualified_name)
        view.response = await ctx.send(embed=embed, view=view)

    @birthdays.command(name="set", aliases=get_aliases("set"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    @app_commands.choices(month=[
        Choice(name="January" ,value=1),
        Choice(name="February ", value=2),
        Choice(name="March", value=3),
        Choice(name="April", value=4),
        Choice(name="May", value=5),
        Choice(name="June", value=6),
        Choice(name="July ", value=7),
        Choice(name="August ", value=8),
        Choice(name="September", value=9),
        Choice(name="October", value=10),
        Choice(name="November", value=11),
        Choice(name="December", value=12),

    ])
    async def set(self, ctx: commands.Context, day:int,month:Choice[int],year:int):
        if  year>datetime.now().year:
            seen = get_lang(ctx.guild.id, "badYear")
        elif date_month(day,month.value):
            seen = get_lang(ctx.guild.id, "badDayMonth").format(month, day)
        else:
            datebr ={"year":year,"month":month.value,"day":day}
            update_user(ctx.author.id, {"dateBirthday": datebr})
            seen = get_lang(ctx.guild.id, "birthdaysSet").format(f"{day} {month.name} {year}")
        if get_user(ctx.author.id).get("serverBirthday") == None:
            update_user(ctx.author.id, {"serverBirthday": []})
        await ctx.send(seen)

    @birthdays.command(name="delete", aliases=get_aliases("delete"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def delete(self, ctx: commands.Context):
        update_user(ctx.author.id ,{"dateBirthday": get_user(ctx.author.id).get("dateBirthday") },"unset")
        await ctx.send(get_lang(ctx.guild.id, "birthdaysDelete"))

    @birthdays.command(name="enable", aliases=get_aliases("enable"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def enable(self, ctx: commands.Context,enable:bool):
        if enable:
            if get_user(ctx.author.id).get('serverBirthday').count(ctx.guild.id) == None :
                a = get_user(ctx.author.id).get('serverBirthday')
                a.append(ctx.author.id)
                update_user(ctx.author.id, {"serverBirthday": a})
            await ctx.send(get_lang(ctx.guild.id, "birthdaysEnableTrue").format(ctx.guild.name))

        else:
            if get_user(ctx.author.id).get('serverBirthday').count(ctx.guild.id) == None :
                a = get_user(ctx.author.id).get('serverBirthday')
                a.remove(ctx.author.id)
                update_user(ctx.author.id, {"serverBirthday": a})
            await ctx.send(get_lang(ctx.guild.id, "birthdaysEnableFalse").format(ctx.guild.name))


    @commands.hybrid_command(name="ping", aliases=get_aliases("ping"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def ping(self, ctx: commands.Context):
        "Test if the bot is alive, and see the delay between your commands and my response."
        print(func.get_birthday(month=1,day=10))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Birthday(bot))
