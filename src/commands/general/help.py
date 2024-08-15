import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.command(
        name="help",
        description="Нужна помощь? Показывает все команды бота."
    )
    async def help_command(self, ctx: commands.Context):
        embed = await self.embed_factory.create_embed(preset='Help', user=ctx.author)
        await ctx.send(embed=embed)

    @commands.slash_command(
        name="help",
        description="Нужна помощь? Показывает все команды бота."
    )
    async def help_slash(self, interaction: disnake.CommandInteraction):
        embed = await self.embed_factory.create_embed(preset='Help', user=interaction.user)
        await interaction.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
