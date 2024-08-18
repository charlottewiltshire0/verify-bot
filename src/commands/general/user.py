import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.slash_command(
        name="user",
        description="Отображает информацию о пользователе."
    )
    async def user_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member = None):
        user = member or interaction.user
        embed = await self.embed_factory.create_embed(preset='User', user=user)
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(User(bot))
