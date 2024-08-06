from __future__ import annotations
from typing import Optional
import disnake
from disnake.ext import commands
from src.module import Yml, loadExtensions
from loguru import logger
from datetime import datetime


__all__ = (
    "Bot"
)


config = Yml('./config/config.yml')
data = config.read()
prefix = data.get('Prefix')


log_filename = f"./logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
logger.add(log_filename, rotation="1 week", level="INFO", format="{time} | {level} | {message}")


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix,
            intents=disnake.Intents.all(),
            chunk_guilds_at_startup=False
        )

        loadExtensions(self, 'src/events', 'src/commands')

    async def success(self, content: str, interaction: disnake.Interaction, ephemeral: Optional[bool]):
        """"SENDING SUCCESS MESSAGE"""
        pass

    async def error(self, content: str, interaction: disnake.Interaction, ephemeral: Optional[bool]):
        """"SENDING ERROR MESSAGE"""
        pass

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