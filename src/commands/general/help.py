import datetime
import os

import disnake
from disnake.ext import commands
from loguru import logger


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        description="Need help? Shows all commands of bot."
    )
    async def help_command(self, ctx: commands.Context):
        embed = disnake.Embed(
            title="📎 Команды:",
            description="- `/player <ник>` - информация об игроке.\n- `/subscribe <канал>` - подписка на новости *("
                        "нужны права админа)*\n- `/un-subscribe` - отписаться от новостей *(нужны права "
                        "админа)*\n\n**🔗 Сcылки:**\n<:reply:1184934756320817243> **Пригласить бота - "
                        "https://dsc.gg/worexgrief-public**\n<:reply:1184934756320817243> **Дискорд сервер - "
                        "https://discord.gg/tAbkmQdAPy**",
            color=0xFFFFFF,
            timestamp=datetime.datetime.now()
        )

        embed.set_author(
            name="🤍 WoreXGrief",
            url="https://discord.gg/xuGTzvtQxs",
        )
        embed.set_footer(
            text="✨ Support Squad of StarStudio"
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
