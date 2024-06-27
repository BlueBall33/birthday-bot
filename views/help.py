import discord
from discord.ext import commands

from funcion import (
    get_lang)
import funcion as func


class HelpDropdown(discord.ui.Select):
    def __init__(self, ctx: discord.Interaction,categorys: list):
        self.view: HelpView

        super().__init__(
            placeholder=get_lang(ctx.guild.id, 'selectCategory'),
            min_values=1, max_values=1,
            options=[
                        discord.SelectOption(emoji="🆕", label=get_lang(ctx.guild.id, 'selectTitleNews'), description=get_lang(ctx.guild.id, 'descriptionNews')),
                    ] + [
                        discord.SelectOption(emoji=emoji, label=get_lang(ctx.guild.id, 'command').format(category),
                                             description=get_lang(ctx.guild.id, 'commandDescription').format(category.lower()))
                        for category, emoji in zip(categorys, ["2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"])
                    ],
            custom_id="select"
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = self.view.build_embed(self.values[0].split(" ")[0])
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ctx: discord.Interaction) -> None:
        super().__init__(timeout=60)

        self.ctx: discord.Interaction = ctx
        self.author: discord.Member = ctx.author
        self.bot: commands.Bot = bot
        self.response: discord.Message = None
        self.categorys: list[str] = [name.capitalize() for name, cog in bot.cogs.items() if
                                     len([c for c in cog.walk_commands()])]

        self.add_item(
             discord.ui.Button(label='Support', emoji=':support:915152950471581696', url=func.settings.invite_link))
        self.add_item(discord.ui.Button(label='Invite', emoji=':invite:915152589056790589',
                                         url='https://discord.com/oauth2/authorize?client_id={}&permissions=2184260928&scope=bot%20applications.commands'.format(
                                               func.tokens.client_id)))
        self.add_item(HelpDropdown(self.ctx, self.categorys))

    async def on_error(self, error, item, interaction) -> None:
        return

    async def on_timeout(self) -> None:
        for child in self.children:
            if child.custom_id == "select":
                child.disabled = True
        try:
            await self.response.edit(view=self)
        except:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> None:
        return interaction.user == self.author

    def build_embed(self, category: str) -> discord.Embed:
        category = category.lower()
        if category == "news":
            embed = discord.Embed(title=get_lang(self.ctx.guild.id,"embedTitleNews"),
                                  url="https://discord.com/channels/",
                                  color=func.settings.embed_color)
            embed.add_field(
                name=get_lang(self.ctx.guild.id,'availableCategories').format(1+len(self.categorys)),
                value="```py\n👉 News\n{}```".format(
                    "".join(f"{i}. {c}\n" for i, c in enumerate(self.categorys, start=2))),
                inline=True
            )

            embed.add_field(name=get_lang(self.ctx.guild.id,'information'), value=get_lang(self.ctx.guild.id,'informationDescription'), inline=True)
            # embed.add_field(name="Get Started",
            #                 value="```Join a voice channel and /play {Song/URL} a song. (Names, Youtube Video Links or Playlist links or Spotify links are supported on Vocard)```",
            #                 inline=False)

            return embed

        embed = discord.Embed(title= get_lang(self.ctx.guild.id,'embedCategoryTitle').format(category.capitalize()  ), color=func.settings.embed_color)
        embed.add_field(name=get_lang(self.ctx.guild.id,'embedCategoryName').format(1 + len(self.categorys)) , value="```py\n" + "\n".join(
            ("👉 " if c == category.capitalize() else f"{i}. ") + c for i, c in
            enumerate(['News'] + self.categorys, start=1)) + "```", inline=True)

        if category == 'tutorial':
            print("S")
        else:
            cog = [c for _, c in self.bot.cogs.items() if _.lower() == category][0]

            commands = [command for command in cog.walk_commands()]
            embed.description = cog.description
            embed.add_field(
                name=get_lang(self.ctx.guild.id, 'embedCategoryAndComands').format(category ,len(commands)) ,
                value="```{}```".format("".join(f"/{command.qualified_name}\n" for command in commands if
                                                not command.qualified_name == cog.qualified_name))
            )

        return embed