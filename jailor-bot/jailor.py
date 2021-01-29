import discord

import modules.functions as functions
import modules.utilities as utilities
import sys

client = discord.Client()


utilities.logger.info(f'Number of arguments: {len(sys.argv)} arguments.')
utilities.logger.info(f'Argument List: {str(sys.argv)}')

try:
    token = functions.authConfig["token"]
except Exception as ex:
    utilities.logger.error(ex)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


utilities.logger.info("Bot listening...")
client.run(token)
