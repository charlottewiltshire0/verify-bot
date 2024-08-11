import importlib
import os
from datetime import datetime
import httpx

import disnake
from disnake.ext import commands
from loguru import logger

from src.module import Yml


class TextFormatter:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    async def format_text(self, text: str, user: disnake.Member = None) -> str:
        placeholders = {
            '{api-ping}': round(self.bot.latency*1000),
            '{bot-pfp}': str(self.bot.user.avatar.url) if self.bot.user.avatar else '',
            '{bot-displayname}': self.bot.user.name,
            '{bot-id}': str(self.bot.user.id),
            '{developer-displayname}': await self.get_user_displayname(671761516265078789),
            '{developer-pfp}': await self.get_user_avatar_url(671761516265078789),
            '{user-pfp}': str(user.avatar.url) if user and user.avatar else '',
            '{user-displayname}': user.display_name if user else '',
            '{user-id}': user.id if user else '',
            '{user-creation}': f"<t:{int(user.created_at.timestamp())}:R>" if user else '',
            '{user-join}': f"<t:{int(user.joined_at.timestamp())}:R>" if user and user.joined_at else '',
            '{total-members-local}': str(user.guild.member_count) if user else '0',
            '{total-members}': self.get_total_members(),
            '{total-messages}': self.get_total_messages(),
            '{version}': get_version(),
            '{uptime}': self.get_uptime(),
        }

        for placeholder, value in placeholders.items():
            text = text.replace(placeholder, str(value))

        return text

    async def get_user_avatar_url(self, user_id: int) -> str:
        try:
            user = await self.bot.fetch_user(user_id)
            return str(user.avatar.url) if user.avatar else ''
        except disnake.NotFound:
            return ''

    async def get_user_displayname(self, user_id: int) -> str:
        try:
            user = await self.bot.fetch_user(user_id)
            return user.display_name
        except disnake.NotFound:
            return ''

    def get_total_members(self) -> str:
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        return str(total_members)

    def get_total_messages(self) -> str:
        tracker = self.bot.get_cog('MessageCreate')
        if tracker:
            return str(tracker.get_total_messages())
        return '0'

    def get_uptime(self) -> str:
        now = datetime.utcnow()
        uptime_duration = now - self.start_time

        days, seconds = uptime_duration.days, uptime_duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return f"{days}d {hours}h {minutes}m {seconds}s"


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


def get_version() -> str:
    config = Yml('./config/config.yml')
    data = config.read()
    version = data['Version']
    request_latest_version = httpx.get(f'https://api.github.com/repos/charlottewiltshire0/verify-bot/releases/latest')
    try:
        currect_version = request_latest_version.json()['tag_name']
    except KeyError:
        return version
    if version != currect_version:
        return f"{version} (Неактуально)"
    else:
        return version

