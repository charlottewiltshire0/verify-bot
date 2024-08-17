import asyncio

import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy.orm import scoped_session

from src.module import Yml, TextFormatter, SessionLocal, Verify


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity_settings = Yml("./config/config.yml").load().get("BotActivitySettings", {})
        self.formatter = TextFormatter()
        self.session = scoped_session(SessionLocal)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user} is now online.")
        await self.add_guilds_to_db()
        await self.update_activity()

    async def update_activity(self):
        if not self.activity_settings.get('Enabled', False):
            return

        # Ensure required settings are present
        required_settings = ('Type', 'Statuses', 'Interval')
        if not all(setting in self.activity_settings for setting in required_settings):
            logger.error(f"Missing required settings for activity: {', '.join(required_settings)}")
            return

        activity_type_str = self.activity_settings.get('Type', 'WATCHING').upper()
        activity_type = {
            'WATCHING': disnake.ActivityType.watching,
            'PLAYING': disnake.ActivityType.playing,
            'COMPETING': disnake.ActivityType.competing
        }.get(activity_type_str, disnake.ActivityType.watching)

        formatted_statuses = await asyncio.gather(
            *[self.formatter.format_text(status, bot=self.bot) for status in self.activity_settings['Statuses']])
        interval = self.activity_settings.get('Interval', 30)

        while True:
            for formatted_status in formatted_statuses:
                activity = disnake.Activity(type=activity_type, name=formatted_status)
                await self.bot.change_presence(activity=activity)
                await asyncio.sleep(interval)

    async def add_guilds_to_db(self):
        session = self.session()
        try:
            for guild in self.bot.guilds:
                existing_entry = session.query(Verify).filter_by(guild=guild.id).first()
                if not existing_entry:
                    new_entry = Verify(
                        guild=guild.id
                    )
                    session.add(new_entry)
            session.commit()
            logger.info("Guilds have been added to the database.")
        except Exception as e:
            logger.error(f"Error occurred while adding guilds to the database: {e}")
            session.rollback()
        finally:
            session.close()


def setup(bot: commands.Bot):
    bot.add_cog(OnReady(bot))
