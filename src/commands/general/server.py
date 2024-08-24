import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.slash_command(
        name="server",
        description="Показать информацию о сервере"
    )
    async def server_slash(self, interaction: disnake.AppCmdInter):
        await interaction.response.defer()
        embed = await self.embed_factory.create_embed(preset='Server', user=interaction.user)
        await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Server(bot))
