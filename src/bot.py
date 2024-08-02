import disnake
from disnake import LoginFailure
from disnake.ext import commands
from loguru import logger

from src.module.utils import loadExtensions

intents = disnake.Intents.all()

bot = commands.Bot(intents=intents, command_prefix='/')

loadExtensions(bot, 'src/events')
loadExtensions(bot, 'src/commands')


def run(token):
    try:
        bot.run(token)
    except LoginFailure:
        logger.error('Your bot token is incorrect! Shutting down...')
