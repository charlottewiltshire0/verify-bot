import importlib
import os
import re
from datetime import datetime, timedelta

import aiohttp
from typing import Optional
import asyncio

import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.exc import NoResultFound, SQLAlchemyError, IntegrityError
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.elements import and_

from src.module import Yml, SessionLocal
from .models import *


class TextFormatter:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.version_cache = None
        self.version_cache_time = None
        self.cache = {}
        self.verify_utils = VerifyUtils()
        self.report_utils = ReportUtils()
        self.mention_utils = MentionUtils()

    async def format_text(self, text: str, user: Optional[disnake.Member] = None, channel: Optional[disnake.TextChannel] = None) -> str:
        placeholders = {
            '{api-ping}': round(self.bot.latency * 1000),
            '{bot-pfp}': self.bot.user.avatar.url if self.bot.user.avatar else '',
            '{bot-displayname}': self.bot.user.name,
            '{bot-id}': str(self.bot.user.id),
            '{prefix}': get_prefix(),
            '{user-pfp}': user.avatar.url if user and user.avatar else '',
            '{user-displayname}': user.display_name if user else '',
            '{user-id}': str(user.id) if user else '',
            '{user-creation}': f"<t:{int(user.created_at.timestamp())}:R>" if user else '',
            '{user-join}': f"<t:{int(user.joined_at.timestamp())}:R>" if user and user.joined_at else '',
            '{user-mention}': f"<@{int(user.id)}>" if user else '',
            '{user-age-days}': str((datetime.utcnow() - user.created_at.replace(tzinfo=None)).days) if user else '',
            '{total-members-local}': str(user.guild.member_count) if user else '0',
            '{total-messages}': self.get_total_messages(),
            '{uptime}': self.get_uptime(),
            '{developer-name}': "\n@charlottewiltshire0\n[WoreXGrief](https://discord.gg/xuGTzvtQxs)",
            '{developer-displayname}': "@charlottewiltshire0",
            '{developer-pfp}': "https://cdn.discordapp.com/attachments/1098234521721241660/1273630739262603295/logo.gif?ex=66bf508f&is=66bdff0f&hm=c19083e5f5e62dab94d9358c72e0fc8b29cc4c6128675ab5f53342b0cbc59317&",
            '{channel-mention}': f"<#{channel.id}>" if channel else '',
            '{verify-status}': self.verify_utils.get_verify_status(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-rejection}': self.verify_utils.get_verify_rejection(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-moderator}': self.verify_utils.get_verify_moderator(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-moderator-id}': self.verify_utils.get_verify_moderator_id(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-lastmoderator}': self.verify_utils.get_verify_last_moderator(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-lastmoderator-id}': self.verify_utils.get_verify_last_moderator_id(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-date}': self.verify_utils.get_verify_date(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-lastdate}': self.verify_utils.get_verify_last_date(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{verify-role}': self.verify_utils.get_verify_role(user_id=user.id, guild_id=user.guild.id) if user else '',
            '{guild-name}': str(user.guild.name) if user else '',
            '{guild-id}': str(user.guild.id) if user else '',
            '{guild-owner-displayname}': str(user.guild.owner) if user else '',
            '{guild-owner}': f"<@{str(user.guild.owner.id)}>" if user else '',
            '{guild-creation}': f"<t:{int(user.guild.created_at.timestamp())}:R>" if user else '',
            '{guild-totalchannels}': str(len(user.guild.channels)) if user else '0',
            '{guild-totaltext}': str(
                len([c for c in user.guild.channels if isinstance(c, disnake.TextChannel)])) if user else '0',
            '{guild-totalvoice}': str(
                len([c for c in user.guild.channels if isinstance(c, disnake.VoiceChannel)])) if user else '0',
            '{guild-totalrole}': str(len(user.guild.roles)) if user else '0',
            '{channelmention}': f'<#{self.mention_utils.get_channel_mention(user.guild.id)}>' if user else '',
            '{date}': datetime.utcnow(),
            '{report-victim}': f'<@{self.report_utils.get_victim_id(victim_id=user.id, guild_id=user.guild.id)}>' if user else '',
            '{report-victim-id}': self.report_utils.get_victim_id(victim_id=user.id, guild_id=user.guild.id) if user else '',
            '{report-perpetrator}': f'<@{self.report_utils.get_perpetrator_id(victim_id=user.id, guild_id=user.guild.id)}>' if user else '',
            '{report-perpetrator-id}': self.report_utils.get_perpetrator_id(victim_id=user.id, guild_id=user.guild.id) if user else '',
            '{report-status}': self.report_utils.get_report_status(victim_id=user.id, guild_id=user.guild.id) if user else '',
            '{report-reason}': self.report_utils.get_reason(victim_id=user.id, guild_id=user.guild.id) if user else '',
            '{report-id}': self.report_utils.get_report_id(victim_id=user.id, guild_id=user.guild.id) if user else '',
        }

        async_replacements = {
            '{total-users}': self.get_total_members(),
            '{version}': self.get_version()
        }

        results = await asyncio.gather(*async_replacements.values())

        for key, result in zip(async_replacements.keys(), results):
            placeholders[key] = result

        for placeholder, value in placeholders.items():
            text = text.replace(placeholder, str(value))

        return text

    async def get_total_members(self) -> str:
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        return str(total_members)

    async def get_version(self) -> str:
        if self.version_cache and (datetime.utcnow() - self.version_cache_time).total_seconds() < 3600:
            return self.version_cache

        config = Yml('./config/config.yml')
        version = config.read().get('Version', 'Unknown')

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.github.com/repos/charlottewiltshire0/verify-bot/releases/latest') as response:
                    response.raise_for_status()
                    current_version = (await response.json()).get('tag_name', version)
            except aiohttp.ClientError:
                return version

        self.version_cache = f"{version} (Неактуально)" if version != current_version else version
        self.version_cache_time = datetime.utcnow()
        return self.version_cache

    def get_total_messages(self) -> str:
        tracker = self.bot.get_cog('MessageCreate')
        return str(tracker.get_total_messages()) if tracker else '0'

    def get_uptime(self) -> str:
        now = datetime.utcnow()
        uptime_duration = now - self.start_time

        days, seconds = uptime_duration.days, uptime_duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return f"{days}д {hours}ч {minutes}м {seconds}с"


class ReportUtils:
    def __init__(self):
        self.session = scoped_session(SessionLocal)

    def get_report_by_id_or_victim(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> Report:
        """Retrieves a report by its ID or by victim ID and guild ID."""
        try:
            if report_id:
                report = self.session.query(Report).filter_by(id=report_id).first()
            else:
                report = self.session.query(Report).filter(
                    and_(Report.victim_id == victim_id, Report.guild_id == guild_id)
                ).first()

            if report:
                self.session.refresh(report)
            return report
        except NoResultFound:
            return None

    def create_report(self, victim_id: int, perpetrator_id: int, guild_id: int, reason: str = None,
                      voice_channel_id: int = None, text_channel_id: int = None) -> Report:
        """Creates a new report if it doesn't already exist."""
        existing_report = self.session.query(Report).filter(
            and_(
                Report.victim_id == victim_id,
                Report.perpetrator_id == perpetrator_id,
                Report.guild_id == guild_id,
                Report.status.in_([ReportStatus.PENDING, ReportStatus.IN_PROGRESS]),
            )
        ).first()

        if existing_report:
            return None

        new_report = Report(
            victim_id=victim_id,
            perpetrator_id=perpetrator_id,
            guild_id=guild_id,
            reason=reason,
            voice_channel_id=voice_channel_id,
            text_channel_id=text_channel_id,
        )
        self.session.add(new_report)
        self.session.commit()
        return new_report

    def get_report_status(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> ReportStatus:
        """Retrieves the status of a report by its ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.status if report else None

    def format_status(self, status: ReportStatus) -> str:
        """Converts a report status to a human-readable string."""
        status_map = {
            ReportStatus.PENDING: "Pending",
            ReportStatus.IN_PROGRESS: "In Progress",
            ReportStatus.RESOLVED: "Resolved",
            ReportStatus.CLOSED: "Closed",
        }
        return status_map.get(status, "Unknown Status")

    def claim_report(self, moderator_id: int, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Marks a report as claimed by a moderator by report ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report:
                report.status = ReportStatus.IN_PROGRESS
                report.is_claimed = True
                report.claimed_by_user_id = moderator_id
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error claiming report: {e}")
        return False

    def close_report(self, moderator_id: int, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Marks a report as closed by a moderator by report ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report and report.status != ReportStatus.CLOSED:
                report.status = ReportStatus.CLOSED
                report.closed_by_user_id = moderator_id
                report.closed_at = func.now()
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error closing report: {e}")
        return False

    def set_message_id(self, message_id: int, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Sets the message ID associated with the report by report ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report:
                report.message_id = message_id
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error setting message ID: {e}")
        return False

    def get_report_id(self, victim_id: int = None, perpetrator_id: int = None, guild_id: int = None) -> int:
        """Retrieves the report ID by victim ID, perpetrator ID, and guild ID."""
        try:
            query = self.session.query(Report.id)

            if victim_id:
                query = query.filter(Report.victim_id == victim_id)
            if perpetrator_id:
                query = query.filter(Report.perpetrator_id == perpetrator_id)
            if guild_id:
                query = query.filter(Report.guild_id == guild_id)

            report_id = query.scalar()
            return report_id
        except NoResultFound:
            return None

    def get_message_id(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> int:
        """Retrieves the message ID associated with the report by report ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.message_id if report else None

    def get_reason(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> str:
        """Retrieves the reason for the report by report ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.reason if report else None

    def get_claimed_by_user_id(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> int:
        """Retrieves the ID of the user who claimed the report by report ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.claimed_by_user_id if report else None

    def get_victim_id(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> int:
        """Retrieves the victim ID from the report by report ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.victim_id if report else None

    def get_perpetrator_id(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> int:
        """Retrieves the perpetrator ID from the report by report ID or by victim ID and guild ID."""
        report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
        return report.perpetrator_id if report else None

    def add_member_to_report(self, member_id: int, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Adds a member to the report's member list by report ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report:
                if member_id in report.member_ids:
                    return False
                if report.victim_id == member_id or report.perpetrator_id == member_id:
                    return False

                if report.member_ids:
                    report.member_ids.append(member_id)
                else:
                    report.member_ids = [member_id]
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding member to report: {e}")
        return False

    def delete_report(self, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Deletes the report by its ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report:
                self.session.delete(report)
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting report: {e}")
        return False

    def remove_member_from_report(self, member_id: int, report_id: int = None, victim_id: int = None, guild_id: int = None) -> bool:
        """Removes the participant from the list of report participants by report ID or by victim ID and guild ID."""
        try:
            report = self.get_report_by_id_or_victim(report_id, victim_id, guild_id)
            if report and report.member_ids:
                if member_id in report.member_ids:
                    report.member_ids.remove(member_id)
                    self.session.commit()
                    return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error removing member from report: {e}")
        return False


class VerifyUtils:
    def __init__(self):
        self.session = scoped_session(SessionLocal)

    def _get_or_create_user(self, user_id: int, guild_id: int) -> VerifyUsers:
        """Получение пользователя по ID или создание нового."""
        user = self.session.query(VerifyUsers).filter_by(user_id=user_id).one_or_none()
        if not user:
            user = VerifyUsers(
                user_id=user_id,
                guild_id=guild_id,
                status=Status.PENDING,
                rejection=0,
                verification_date=None
            )
            self.session.add(user)
            self.session.commit()
        return user

    def get_verify_status(self, user_id: int, guild_id: int) -> str:
        """Получение статуса верификации пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return self.format_status(user.status)

    def get_verify_rejection(self, user_id: int, guild_id: int) -> int:
        """Получение количества отказов пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return user.rejection

    def get_verify_moderator(self, user_id: int, guild_id: int) -> str:
        """Получение упоминания модератора, который верифицировал пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        if user.moder_id:
            return f"<@{user.moder_id}>"
        return "`Нету`"

    def get_verify_moderator_id(self, user_id: int, guild_id: int) -> Optional[int]:
        """Получение ID модератора, который верифицировал пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return user.moder_id

    def get_verify_last_moderator(self, user_id: int, guild_id: int) -> str:
        """Получение упоминания модератора, который верифицировал пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        if user.last_moder_id:
            return f"<@{user.last_moder_id}>"
        return "`Нету`"

    def get_verify_last_moderator_id(self, user_id: int, guild_id: int) -> Optional[int]:
        """Получение ID модератора, который верифицировал пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return user.last_moder_id

    def get_verify_date(self, user_id: int, guild_id: int) -> Optional[datetime]:
        """Получение даты верификации пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return user.verification_date

    def get_verify_last_date(self, user_id: int, guild_id: int) -> Optional[datetime]:
        """Получение даты верификации пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        return user.last_verification_date

    def get_verify_role(self, user_id: int, guild_id: int) -> Optional[int]:
        user = self._get_or_create_user(user_id, guild_id)
        return user.role_id

    def verify_user(self, user_id: int, guild_id: int, moder_id: Optional[int] = None):
        """Утверждение пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        user.status = Status.APPROVED
        user.moder_id = moder_id
        user.verification_date = datetime.utcnow()
        self.session.commit()

    def last_moder(self, user_id: int, guild_id: int, moder_id: Optional[int] = None):
        """Утверждение пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        user.last_moder_id = moder_id
        user.last_verification_date = datetime.utcnow()
        self.session.commit()

    def unverify_user(self, user_id: int, guild_id: int):
        """Отмена верификации пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        user.status = Status.PENDING
        user.moder_id = None
        user.verification_date = None
        user.role_id = None
        self.session.commit()

    def give_rejection(self, user_id: int, guild_id: int):
        """Добавление отказа пользователю."""
        user = self._get_or_create_user(user_id, guild_id)
        user.rejection += 1
        self.session.commit()

    def remove_rejection(self, user_id: int, guild_id: int):
        """Удаление отказа у пользователя."""
        user = self._get_or_create_user(user_id, guild_id)
        if user.rejection > 0:
            user.rejection -= 1
            self.session.commit()

    def set_rejection(self, user_id: int, guild_id: int, rejection_count: int):
        """Установка количества отказов пользователю."""
        user = self._get_or_create_user(user_id, guild_id)
        user.rejection = rejection_count
        self.session.commit()

    def set_role(self, user_id: int, guild_id: int, role_id: int):
        """Установка количества отказов пользователю."""
        user = self._get_or_create_user(user_id, guild_id)
        user.role_id = role_id
        self.session.commit()

    def format_status(self, status: Status) -> str:
        """Форматирование статуса в понятный вид."""
        status_mapping = {
            Status.PENDING: "<:pending:1274024354610544752> (Пройдите верификацию!)",
            Status.APPROVED: "<a:approved:1274023693357420628>",
            Status.REJECTED: "<a:deny:1274024159889981502>"
        }
        return status_mapping.get(status, "<a:404:1274017785541955676>")

    def is_user_verified(self, user_id: int, guild_id: int) -> bool:
        user = self._get_or_create_user(user_id, guild_id)
        return user and user.status == Status.APPROVED


class BanUtils:
    def __init__(self):
        self.session = scoped_session(SessionLocal)

    def record_ban(self, member, guild, moderator, reason):
        session = self.session()
        try:
            ban = Ban(
                user_id=member.id,
                guild_id=guild.id,
                ban_date=datetime.utcnow(),
                reason=reason,
                moderator_id=moderator.id,
                status=BanStatus.ACTIVE
            )
            session.add(ban)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка записи бана в базу данных: {e}")
        finally:
            session.close()

    def parse_time(self, time_str):
        pattern = re.compile(r'((?P<hours>\d+)h)?\s*((?P<minutes>\d+)m)?')
        match = pattern.match(time_str)
        if not match:
            return None
        time_params = {name: int(param) for name, param in match.groupdict().items() if param}
        return timedelta(**time_params)


def loadExtensions(bot: commands.Bot, *directories: str):
    """Load extensions (cogs) from specified directories."""
    for directory in directories:
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} does not exist.")
            continue

        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                try:
                    importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
                    bot.load_extension(f"{directory.replace('/', '.')}.{module_name}")
                    logger.info(f"Loaded extension: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load extension {module_name}: {e}")


def get_prefix() -> str:
    return '/'


class MentionUtils:
    def __init__(self):
        self.session = scoped_session(SessionLocal)

    def get_channel_mention(self, guild_id):
        """Получить канал channel_mention для указанного guild_id."""
        try:
            verify_entry = self.session.query(Verify).filter(Verify.guild == guild_id).one_or_none()
            return verify_entry.channel_mention if verify_entry else None
        except Exception as e:
            logger.error(f"Error fetching channel_mention: {e}")
            return None

    def add_channel_mention(self, guild_id, channel_mention) -> bool:
        try:
            verify_entry = self.session.query(Verify).filter(Verify.guild == guild_id).one_or_none()
            if verify_entry:
                if verify_entry.channel_mention:
                    return False
                verify_entry.channel_mention = channel_mention
            else:
                new_entry = Verify(guild=guild_id, channel_mention=channel_mention)
                self.session.add(new_entry)
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding channel_mention: {e}")
            return False

    def remove_channel_mention(self, guild_id):
        try:
            verify_entry = self.session.query(Verify).filter(Verify.guild == guild_id).one_or_none()
            if verify_entry and verify_entry.channel_mention:
                verify_entry.channel_mention = None
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error removing channel_mention: {e}")
            return False

    def set_channel_mention(self, guild_id, channel_mention):
        try:
            verify_entry = self.session.query(Verify).filter(Verify.guild == guild_id).one_or_none()
            if verify_entry:
                verify_entry.channel_mention = channel_mention
            else:
                new_entry = Verify(guild=guild_id, channel_mention=channel_mention)
                self.session.add(new_entry)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error setting channel_mention: {e}")
            return False


def get_button_style(color: str) -> disnake.ButtonStyle:
    color_map = {
        "Blurple": disnake.ButtonStyle.blurple,
        "Grey": disnake.ButtonStyle.grey,
        "Green": disnake.ButtonStyle.green,
        "Red": disnake.ButtonStyle.red,
    }
    return color_map.get(color, disnake.ButtonStyle.grey)


async def log_action(bot: commands.Bot, logging_channel_id: int, embed_factory, action: str, member: disnake.Member, color: str = None):
    if not logging_channel_id:
        return

    channel = bot.get_channel(logging_channel_id)
    if channel:
        embed = await embed_factory.create_embed(preset=action, user=member, color_type=color)
        await channel.send(embed=embed)
    else:
        print(f"Logging channel with ID {logging_channel_id} not found.")


async def send_embed_to_member(embed_factory, member, preset, color_type):
    embed = await embed_factory.create_embed(preset=preset, color_type=color_type)
    try:
        await member.send(embed=embed)
    except Exception as e:
        logger.error(f"Failed to send DM to {member}: {e}")