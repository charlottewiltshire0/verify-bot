import datetime
import os

import disnake
from disnake.ext import commands
from loguru import logger

from src.module import EmbedFactory


class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.command(
        name="about",
        description=""
    )
    async def help_command(self, ctx: commands.Context):
        embed = self.embed_factory.create_embed(preset='About', user=ctx.author)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(About(bot))
