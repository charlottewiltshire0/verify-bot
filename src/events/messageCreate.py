import disnake
from disnake.ext import commands


class MessageCreate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.total_messages = 0

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if not message.author.bot:
            self.total_messages += 1

    def get_total_messages(self) -> int:
        return self.total_messages


def setup(bot: commands.Bot):
    bot.add_cog(MessageCreate(bot))
