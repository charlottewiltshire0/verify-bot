import importlib
import os
from datetime import datetime

import aiohttp
from typing import Optional
import asyncio

import disnake
from disnake.ext import commands
from loguru import logger
from sqlalchemy.orm import Session

from src.module import Yml
from .models import *


class TextFormatter:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.version_cache = None
        self.version_cache_time = None
        self.cache = {}

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
            '{total-members-local}': str(user.guild.member_count) if user else '0',
            '{total-messages}': self.get_total_messages(),
            '{uptime}': self.get_uptime(),
            '{developer-name}': "[WoreXGrief](https://discord.gg/xuGTzvtQxs)\n@charlottewiltshire0\n@snezhokyt",
            '{developer-displayname}': "WoreXGrief",
            '{developer-pfp}': "https://cdn.discordapp.com/attachments/1098234521721241660/1273630739262603295/logo.gif?ex=66bf508f&is=66bdff0f&hm=c19083e5f5e62dab94d9358c72e0fc8b29cc4c6128675ab5f53342b0cbc59317&",
            '{channel-mention}': f"<#{channel.id}>" if channel else '',
        }

        async_replacements = {
            '{total-users}': self.get_total_members(),
            '{version}': self.get_version(),
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
    config = Yml('./config/config.yml')
    return config.read().get('Prefix', 'Unknown')


def add_channel_mention(db: Session, guild_id: int, channel_mention: int):
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


def remove_channel_mention(db: Session, guild_id: int):
    verify_entry = db.query(Verify).filter_by(guild=guild_id).first()
    if verify_entry:
        verify_entry.channel_mention = None
        db.commit()


def set_channel_mention(db: Session, guild_id: int, channel_mention: int):
    verify_entry = db.query(Verify).filter_by(guild=guild_id).first()
    if verify_entry:
        verify_entry.channel_mention = channel_mention
    else:
        verify_entry = Verify(guild=guild_id, channel_mention=channel_mention)
        db.add(verify_entry)
    db.commit()
