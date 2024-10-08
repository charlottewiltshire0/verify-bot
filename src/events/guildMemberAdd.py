import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session

from src.module import SessionLocal, VerifyUsers, Verify, Status, MentionUtils, EmbedFactory


class GuildMemberAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = scoped_session(SessionLocal)
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.mention_utils = MentionUtils()

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        logger.info(f"{member.name} joined {member.guild}")

        guild_id = member.guild.id
        channel_id = self.mention_utils.get_channel_mention(guild_id)

        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                embed = await self.embed_factory.create_embed(preset='MemberJoin', user=member)
                await channel.send(embed=embed)

        await self.add_user_to_db(member)

    async def add_user_to_db(self, member):
        session = self.session()
        try:
            existing_user = session.query(VerifyUsers).filter_by(user_id=member.id, guild_id=member.guild.id).first()
            if not existing_user:
                verify_entry = session.query(Verify).filter_by(guild=member.guild.id).first()
                if verify_entry:
                    new_user = VerifyUsers(
                        user_id=member.id,
                        guild_id=member.guild.id,
                        status=Status.PENDING
                    )
                    session.add(new_user)
                    session.commit()
                    logger.info(f"User {member} has been added to the database.")
                else:
                    logger.warning(f"Guild {member.guild.id} not found in the Verify table. User {member.id} not added.")
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while adding user {member} to the database: {e}")
            session.rollback()
        finally:
            session.close()


def setup(bot):
    bot.add_cog(GuildMemberAdd(bot))
