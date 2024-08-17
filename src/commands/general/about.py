import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml')

    @commands.slash_command(
        name="about",
        description="Основная информация о боте.",
    )
    async def about_slash(self, interaction: disnake.AppCmdInter):
        embed = await self.embed_factory.create_embed(preset='About', user=interaction.user, bot=self.bot)
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(About(bot))
