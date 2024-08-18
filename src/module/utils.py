import importlib
import os
from datetime import datetime

import aiohttp
from typing import Optional
import asyncio

import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session
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

    def create_report(self, victim_id, perpetrator_id, guild_id, voice_id=None, channel_id=None):
        existing_report = self.session.execute(
            select(Report).where(
                and_(
                    Report.victim_id == victim_id,
                    Report.perpetrator_id == perpetrator_id,
                    Report.guild_id == guild_id,
                    Report.status.in_([ReportStatus.PENDING, ReportStatus.IN_PROGRESS])
                )
            )
        ).scalar_one_or_none()

        if existing_report:
            return None

        new_report = Report(
            victim_id=victim_id,
            perpetrator_id=perpetrator_id,
            guild_id=guild_id,
            voice_id=voice_id,
            channel_id=channel_id
        )
        self.session.add(new_report)
        self.session.commit()
        return new_report

    def get_report_status(self, report_id):
        try:
            report = self.session.execute(
                select(Report).where(Report.id == report_id)
            ).scalar_one()
            return report.status
        except NoResultFound:
            return None

    def format_status(self, status):
        status_map = {
            ReportStatus.PENDING: "Pending",
            ReportStatus.IN_PROGRESS: "In Progress",
            ReportStatus.RESOLVED: "Resolved",
            ReportStatus.CLOSED: "Closed"
        }
        return status_map.get(status, "Unknown Status")

    def claim_report(self, report_id: int, moderator_id: int) -> bool:
        try:
            report = self.session.query(Report).filter_by(id=report_id).first()
            if report:
                report.status = ReportStatus.IN_PROGRESS
                report.claimed = True
                report.claimed_by = moderator_id
                self.session.commit()
                return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.info(f"Ошибка базы данных: {e}")
        return False

    def get_moderator_id(self, report_id):
        try:
            report = self.session.execute(
                select(Report).where(Report.id == report_id)
            ).scalar_one()
            return report.claimed_by
        except NoResultFound:
            return None

    def get_victim_id(self, report_id):
        try:
            report = self.session.execute(
                select(Report).where(Report.id == report_id)
            ).scalar_one()
            return report.victim_id
        except NoResultFound:
            return None

    def get_perpetrator_id(self, report_id):
        try:
            report = self.session.execute(
                select(Report).where(Report.id == report_id)
            ).scalar_one()
            return report.perpetrator_id
        except NoResultFound:
            return None

    def add_member_to_report(self, report_id, member_id):
        report = self.session.execute(
            select(Report).where(Report.id == report_id)
        ).scalar_one_or_none()

        if report:
            if report.members_id:
                report.members_id.append(member_id)
            else:
                report.members_id = [member_id]
            self.session.commit()
            return True
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


def add_channel_mention(db: Session, guild_id: int, channel_mention: int) -> bool:
    verify_entry = db.query(Verify).filter_by(guild=guild_id).first()
    if verify_entry:
        if verify_entry.channel_mention == channel_mention:
            return False
        verify_entry.channel_mention = channel_mention
    else:
        verify_entry = Verify(guild=guild_id, channel_mention=channel_mention)
        db.add(verify_entry)
    db.commit()
    return True


def remove_channel_mention(db: Session, guild_id: int) -> bool:
    verify_entry = db.query(Verify).filter_by(guild=guild_id).first()
    if verify_entry and verify_entry.channel_mention:
        verify_entry.channel_mention = None
        db.commit()
        return True
    return False


def set_channel_mention(db: Session, guild_id: int, channel_mention: int):
    verify_entry = db.query(Verify).filter_by(guild=guild_id).first()
    if verify_entry:
        verify_entry.channel_mention = channel_mention
    else:
        verify_entry = Verify(guild=guild_id, channel_mention=channel_mention)
        db.add(verify_entry)
    db.commit()


def get_button_style(color: str) -> disnake.ButtonStyle:
    color_map = {
        "Blurple": disnake.ButtonStyle.blurple,
        "Grey": disnake.ButtonStyle.grey,
        "Green": disnake.ButtonStyle.green,
        "Red": disnake.ButtonStyle.red,
    }
    return color_map.get(color, disnake.ButtonStyle.grey)