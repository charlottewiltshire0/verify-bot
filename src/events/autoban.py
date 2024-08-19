from datetime import datetime

import disnake
from disnake.ext import commands, tasks
from loguru import logger
from sqlalchemy.orm import scoped_session

from src.module import SessionLocal, Yml, EmbedFactory, VerifyUtils, send_embed_to_member, log_action


class AutoBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.session = scoped_session(SessionLocal)
        self.verify_utils = VerifyUtils()

        self.autoban_settings = Yml("./config/config.yml").load().get("AutoBan", {})
        self.autoban_settings_verify = self.autoban_settings.get("VerifyRejection", {})
        self.autoban_settings_no_avatar = self.autoban_settings.get("NoAvatar", {})
        self.autoban_settings_account_age = self.autoban_settings.get("AccountAge", {})

        self.minimum_account_age = self.autoban_settings_account_age.get("MinimumAccountAge", 7)
        self.trigger_action_account_age = self.autoban_settings_account_age.get('TriggerAction', 'KICK')

        self.trigger_action_no_avatar = self.autoban_settings_no_avatar.get('TriggerAction', 'KICK')
        self.dm_user_no_avatar = self.autoban_settings_no_avatar.get('DMUser', True)

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('AutoBan', {}).get('Enabled',
                                                                                                          False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('AutoBan', {})
                                      .get('ChannelID', 0))

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if self.autoban_settings_account_age.get('Enabled', False):
            await self.check_account_age(member)
        if self.autoban_settings_no_avatar.get('Enabled', False):
            await self.check_no_avatar(member)

    @tasks.loop(minutes=5)
    async def check_rejection(self):
        guilds = self.bot.guilds
        for guild in guilds:
            for member in guild.members:
                if not member.bot:
                    if self.autoban_settings_verify.get('Enabled', False):
                        await self.check_verify_rejection(member)

    async def check_account_age(self, member):
        creation_date = member.created_at
        current_time = datetime.now(creation_date.tzinfo)
        age_days = (current_time - creation_date).days

        if age_days < self.minimum_account_age:
            match self.trigger_action_account_age:
                case 'KICK':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    await member.kick(reason='Ваш аккаунт младше минимально требуемого возраста для проверки.')
                    logger.info(f'Kicked {member.name} for having an account age below {self.minimum_account_age} days.')

                case 'TIMEOUT':
                    if self.logging_enabled:
                        await member.timeout(duration=3600, reason="Ваш аккаунт младше минимально требуемого возраста для проверки.")
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")

                case 'BAN':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    await member.ban(reason='Ваш аккаунт младше минимально требуемого возраста для проверки.')
                    logger.info(f'Banned {member.name} for having an account age below {self.minimum_account_age} days.')

                case 'LOG':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    logger.info(f'Logged {member.name} for having an account age below {self.minimum_account_age} days.')

    async def check_verify_rejection(self, member):
        rejection_count = self.verify_utils.get_verify_rejection(user_id=member.id, guild_id=member.guild.id)
        if rejection_count >= self.autoban_settings_verify.get('MaxRejection', 5):

            if self.autoban_settings_verify.get('DMUser', False):
                await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                           preset="AutoBanVerifyRejection", color_type="Error")

            punishment = self.autoban_settings_verify['AutoPunishments'].get(rejection_count)

            match punishment:
                case "KICK":
                    try:
                        await member.kick(reason="Ваша верификация была успешно удалена. Если у вас есть вопросы или вы хотите снова пройти верификацию, обратитесь к модераторам.")
                    except Exception as e:
                        logger.error(f"Failed to kick {member}: {e}")

                case "TIMEOUT":
                    try:
                        await member.timeout(duration=3600, reason="Ваша верификация была успешно удалена. Если у вас есть вопросы или вы хотите снова пройти верификацию, обратитесь к модераторам.")
                    except Exception as e:
                        logger.error(f"Failed to timeout {member}: {e}")

                case "BAN":
                    try:
                        await member.ban(reason="Ваша верификация была успешно удалена. Если у вас есть вопросы или вы хотите снова пройти верификацию, обратитесь к модераторам.")
                    except Exception as e:
                        logger.error(f"Failed to ban {member}: {e}")

                case "LOG":
                    logger.info(f"{member} has been rejected {rejection_count} times and will be logged.")
                    await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                     embed_factory=self.embed_factory,
                                     action='LogAutoBanRejection', member=member, color="Error")

    async def check_no_avatar(self, member: disnake.Member):
        if member.avatar is None:
            if self.dm_user_no_avatar:
                await send_embed_to_member(embed_factory=self.embed_factory, member=member, color_type="Error",
                                           preset="NoAvatar")

            match self.trigger_action_no_avatar:
                case 'KICK':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanNoAvatar', member=member, color="Error")
                    await member.kick(reason='Аватар не установлен.')
                    logger.info(f'Kicked {member.name} for not having an avatar.')

                case 'TIMEOUT':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    await member.timeout(duration=3600, reason="Аватар не установлен.")

                case 'BAN':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    await member.ban(reason='Аватар не установлен.')
                    logger.info(f'Banned {member.name} for not having an avatar.')

                case 'LOG':
                    if self.logging_enabled:
                        await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                         embed_factory=self.embed_factory,
                                         action='LogAutoBanAccountAge', member=member, color="Error")
                    logger.info(f'Logged {member.name} for not having an avatar.')


def setup(bot):
    bot.add_cog(AutoBanCog(bot))
