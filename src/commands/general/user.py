from disnake.ext import commands

from src.module import EmbedFactory


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.command(
        name="user",
        description="Отображает информацию о пользователе."
    )
    async def help_command(self, ctx: commands.Context):
        embed = await self.embed_factory.create_embed(preset='User', user=ctx.author)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(User(bot))
