from disnake import DiscordException
from yaml import YAMLError

from src.module.yml import Yml
from src.bot import run

try:
    config = Yml('./config/config.yml')
    lang = Yml('./config/lang.yml')
    embeds = Yml('./config/embeds.yml')
except YAMLError:
    print("An error has occured while loading the config or lang file. Bot shutting down...")
    exit(1)

data = config.read()
token = data.get('Token')
prefix = data.get('Prefix')

if __name__ == "__main__":
    try:
        run(
            token=token
        )
    except DiscordException:
        print("Environment variables not set!")