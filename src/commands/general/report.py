import disnake
from disnake.ext import commands

from src.modals.reportModals import ReportModal
from src.module import EmbedFactory


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.slash_command(
        name="report",
        description="Сообщить о проблеме или нарушении"
    )
    async def report_slash(self, interaction: disnake.AppCmdInter):
        modal = ReportModal()
        await interaction.response.send_modal(modal=modal)


def setup(bot: commands.Bot):
    bot.add_cog(Report(bot))
