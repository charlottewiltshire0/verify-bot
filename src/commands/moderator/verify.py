import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.slash_command(
        name="verify",
        description="Верифицировать пользователя на сервере"
    )
    async def verify_slash(self, interaction: disnake.AppCmdInter):
        pass

    @verify_slash.sub_command(
        name="add",
        description="Добавить пользователя в верифицированные"
    )
    async def verify_add_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member):
        embed = await self.embed_factory.create_embed(preset='User', user=member)
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)

    @verify_slash.sub_command(
        name="remove",
        description="Удалить пользователя из верифицированных"
    )
    async def verify_remove_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member):
        embed = await self.embed_factory.create_embed(preset='User', user=member)
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Verify(bot))
