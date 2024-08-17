import disnake
from disnake.ext import commands

from src.module import EmbedFactory


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    @commands.command(
        name="server",
        description="Показать информацию о сервере"
    )
    async def user_command(self, ctx: commands.Context, member: disnake.Member = None):
        user = member or ctx.author
        embed = await self.embed_factory.create_embed(preset='Server', user=user)
        await ctx.send(embed=embed)

    @commands.slash_command(
        name="server",
        description="Показать информацию о сервере"
    )
    async def user_slash(self, interaction: disnake.CommandInteraction, member: disnake.Member = None):
        user = member or interaction.user
        embed = await self.embed_factory.create_embed(preset='Server', user=user)
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Server(bot))
