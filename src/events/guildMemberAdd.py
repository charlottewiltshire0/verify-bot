# from datetime import datetime
#
# import disnake
# from disnake.ext import commands
# from sqlalchemy import select
# from sqlalchemy.orm import scoped_session
#
# from src.module import SessionLocal, Verify, VerifyUsers
#
#
# class GuildMemberAdd(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.session = scoped_session(SessionLocal)
#
#     @commands.Cog.listener()
#     async def on_member_join(self, member: disnake.Member):
#         print(f"{member.name} joined {member.guild}")
#         with self.session() as session:
#             verify_obj = session.execute(
#                 select(Verify).where(Verify.guild == member.guild.id)
#             ).scalars().one_or_none()
#
#             if not verify_obj:
#                 print(f"No verify object found for guild: {member.guild.id}")
#                 return
#
#             user_record = session.execute(
#                 select(VerifyUsers).where(VerifyUsers.user_id == member.id)
#             ).scalars().one_or_none()
#
#             if not user_record:
#
#                 new_user = VerifyUsers(
#                     user_id=member.id,
#                     moder_id=None,
#                     verify_id=verify_obj.id,
#                     status="pending",
#                     rejection=0,
#                     verification_date=datetime.utcnow()
#                 )
#                 session.add(new_user)
#                 session.commit()
#                 print(f"Added new user to database: {member.id}")
#             else:
#                 print(f"User already exists in the database: {member.id}")
#
#
# def setup(bot):
#     bot.add_cog(GuildMemberAdd(bot))
