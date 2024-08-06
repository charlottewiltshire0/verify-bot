from __future__ import annotations
from typing import Optional
import disnake
from disnake.ext import commands
from src.module import Yml
import asyncio

__all__ = (
    "Bot"
)

config = Yml('./config/config.yml')
data = config.read()
prefix = data.get('Prefix')


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix,
            intents=disnake.Intents.all(),
            chunk_guilds_at_startup=False
        )

    async def success(self, content: str, interaction: disnake.Interaction, ephemeral: Optional[bool]):
        """"SENDING SUCCESS MESSAGE"""
        pass

    async def error(self, content: str, interaction: disnake.Interaction, ephemeral: Optional[bool]):
        """"SENDING ERROR MESSAGE"""
        pass

    async def __aenter__(self):
        token = data.get('Token')
        if not token:
            raise ValueError("Discord bot token not found in config.yml")

        await self.login(token)
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

# loadExtensions(bot, 'src/events')
# loadExtensions(bot, 'src/commands')
