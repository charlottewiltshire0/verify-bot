from __future__ import annotations

from asyncio import run

from loguru import logger
from src import Bot


async def main():
    async with Bot() as bot:
        logger.info("Starting bot...")
        await bot.start(reconnect=True)


if __name__ == '__main__':
    run(main())
