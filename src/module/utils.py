import os
from loguru import logger


def loadExtensions(bot, directory):
    """Load all extensions from a given directory."""
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('_'):
            extension_name = f"{directory.replace('/', '.')}.{filename[:-3]}"
            try:
                bot.load_extension(extension_name)
                logger.info(f"Loaded extension: {extension_name}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension_name}: {e}")
