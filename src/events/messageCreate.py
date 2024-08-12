import disnake
from disnake.ext import commands
from sqlalchemy.orm import Session

from src.module import SessionLocal, Settings


class MessageCreate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Session = SessionLocal()
        self.total_messages = self.get_db_total_messages()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if not message.author.bot:
            self.total_messages += 1
            self.update_db_total_messages(self.total_messages)

    def get_total_messages(self) -> int:
        return self.total_messages

    def get_db_total_messages(self) -> int:
        settings = self.db.query(Settings).first()
        if settings is None:
            settings = Settings(total_message=0)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings.total_message

    def update_db_total_messages(self, total: int):
        settings = self.db.query(Settings).first()
        if settings:
            settings.total_message = total
            self.db.commit()

    def cog_unload(self):
        self.db.close()


def setup(bot: commands.Bot):
    bot.add_cog(MessageCreate(bot))
