from __future__ import annotations

import asyncio
from yaml import YAMLError
from loguru import logger

from src import Bot
from src.module import Yml

try:
    config = Yml('./config/config.yml')
    lang = Yml('./config/lang.yml')
    embeds = Yml('./config/embeds.yml')
except YAMLError:
    logger.error("An error has occured while loading the config or lang file. Bot shutting down...")
    exit(1)


async def main():
    async with Bot() as bot:
        logger.info("Starting bot...")
        await bot.start(reconnect=True)


if __name__ == '__main__':
    asyncio.run(main())
