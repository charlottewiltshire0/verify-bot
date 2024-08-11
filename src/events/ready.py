from disnake.ext import commands
from loguru import logger


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user} is now online.")


def setup(bot: commands.Bot):
    bot.add_cog(OnReady(bot))
