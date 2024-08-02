import disnake
from disnake.ext import commands

from src.module.utils import loadExtensions

intents = disnake.Intents.all()

bot = commands.Bot(intents=intents, command_prefix='/')

loadExtensions(bot, 'src/events')
loadExtensions(bot, 'src/commands')

def run(token):
    bot.run(token)
