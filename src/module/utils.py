import os
import importlib
from disnake.ext import commands
from loguru import logger


def loadExtensions(bot: commands.Bot, *directories: str):
    """Load extensions (cogs) from specified directories."""
    for directory in directories:
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} does not exist.")
            continue

        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]  # Remove the .py extension
                try:
                    # Import the module
                    importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
                    # Add the cog to the bot
                    bot.load_extension(f"{directory.replace('/', '.')}.{module_name}")
                    logger.info(f"Loaded extension: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load extension {module_name}: {e}")
