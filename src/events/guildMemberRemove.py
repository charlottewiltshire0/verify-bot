import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session

from src.module import SessionLocal, VerifyUsers, Verify, Status


class GuildMemberRemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = scoped_session(SessionLocal)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        logger.info(f"{member.name} has left {member.guild}")
        await self.remove_user_from_db(member)

    async def remove_user_from_db(self, member):
        session = self.session()
        try:
            user_to_delete = session.query(VerifyUsers).filter_by(user_id=member.id, guild_id=member.guild.id).first()
            if user_to_delete:
                session.delete(user_to_delete)
                session.commit()
                logger.info(f"User {member} has been removed from the database.")
            else:
                logger.warning(f"User {member.id} not found in the database.")
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while removing user {member} from the database: {e}")
            session.rollback()
        finally:
            session.close()


def setup(bot):
    bot.add_cog(GuildMemberRemove(bot))
