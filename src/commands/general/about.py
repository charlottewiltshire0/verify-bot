import datetime
import os

import disnake
from disnake.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="help",
        description="Need help? Shows all commands of bot."
    )
    async def help_command(self, inter: disnake.ApplicationCommandInteraction):
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
            icon_url=os.environ["BOT_ICON_URL"],
        )
        embed.set_footer(
            text="✨ Support Squad of StarStudio"
        )
        await inter.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
    logger.info(f"Extension {__name__} is ready")
