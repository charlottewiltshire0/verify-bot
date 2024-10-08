from __future__ import annotations
from typing import Optional
import disnake
from disnake.ext import commands
from src.module import Yml, loadExtensions, init_db
from loguru import logger
from datetime import datetime


__all__ = (
    "Bot"
)


config = Yml('./config/config.yml')
data = config.read()


init_db()


log_filename = f"./logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
logger.add(log_filename, rotation="1 week", level="INFO", format="{time} | {level} | {message}")


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=disnake.Intents.all(),
            help_command=None,
            chunk_guilds_at_startup=False
        )

        loadExtensions(self, 'src/events', 'src/commands/moderator', 'src/commands/general', 'src/commands/owner')

    async def __aenter__(self):
        token = data.get('BotToken')
        if not token:
            logger.error("Your bot token is incorrect! Shutting down...")
            raise ValueError("Your bot token is incorrect! Shutting down...")

        logger.info("Logging in...")
        await self.login(token)
        logger.info("Connecting...")
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.info("Closing connection...")
        await self.close()
        if exc_type:
            logger.error(f"An error occurred: {exc_type.__name__} - {exc}")