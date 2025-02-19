import discord
import funcion as func
from datetime import datetime

from discord.ext import commands, tasks
from addons import Placeholders


class Task(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.activity_update.start()
        self.birthdays.start()


        self.act_type = {
            "play": discord.ActivityType.playing,
            "listen": discord.ActivityType.listening,
            "watch": discord.ActivityType.watching,
            "stream": discord.ActivityType.streaming
        }
        self.current_act = 0
        self.placeholder = Placeholders(bot)

    def cog_unload(self):
        self.activity_update.cancel()
        self.birthdays.cancel()


    @tasks.loop(minutes=10.0)
    async def activity_update(self):
        await self.bot.wait_until_ready()

        try:
            act_data = func.settings.activity[(self.current_act + 1) % len(func.settings.activity) - 1]

            act_original = self.bot.activity
            act_type = self.act_type.get(list(act_data.keys())[0].lower(), discord.ActivityType.playing)
            act_name = self.placeholder.replace(list(act_data.values())[0])

            if act_original.type != act_type or act_original.name != act_name:
                new_act = discord.Activity(type=act_type, name=act_name)
                await self.bot.change_presence(activity=new_act)
                self.current_act = (self.current_act + 1) % len(func.settings.activity)

        except:
            pass

    @tasks.loop(minutes=10.0)
    async def birthdays(self):
        await self.bot.wait_until_ready()
        user = func.get_birthday(datetime.now().month,datetime.now().day)
        for use in user:
            for guild_id in use.get("serverBirthday"):
                try:
                    chanalID = func.get_settings(guild_id).get("birthdaysChanal")
                    chanal = self.bot.get_channel(chanalID)
                    await  chanal.send(func.get_lang(guild_id, "birthdaysWishes").format(use.get("_id")))
                except:
                    pass



async def setup(bot: commands.Bot):
    await bot.add_cog(Task(bot))