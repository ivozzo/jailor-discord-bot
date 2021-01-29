import discord

import modules.configuration as configuration
import modules.utilities as utilities
import sys

client = discord.Client()

try:
    configuration.init(sys.argv[1])
    utilities.init_logger(configuration.logging["level"])
    token = configuration.auth["token"]
except Exception as ex:
    utilities.logger.error(ex)

utilities.logger.debug(f'Number of arguments: {len(sys.argv)} arguments.')
utilities.logger.debug(f'Argument List: {str(sys.argv)}')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


utilities.logger.info("Bot listening...")
client.run(token)
