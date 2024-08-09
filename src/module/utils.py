import os
import importlib

import disnake
from disnake.ext import commands
from loguru import logger


class TextFormatter:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def format_text(self, text: str, user: disnake.Member = None) -> str:
        placeholders = {
            '{api-ping}': round(self.bot.latency*1000),
            '{bot-pfp}': str(self.bot.user.avatar.url) if self.bot.user.avatar else '',
            '{bot-displayname}': self.bot.user.name,
            '{bot-id}': str(self.bot.user.id),
            '{developer-displayname}': '<@671761516265078789>',
            '{developer-pfp}': '<@671761516265078789>',
            '{user-pfp}': str(user.avatar.url) if user and user.avatar else '',
            '{user-displayname}': user.display_name if user else '',
        }

        for placeholder, value in placeholders.items():
            text = text.replace(placeholder, value)

        return text

    # def get_uptime(self) -> str:
    #     delta = disnake.utils.utcnow() - self.bot.start_time
    #     return str(delta).split('.')[0]


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
