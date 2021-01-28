import modules.functions as functions

import modules.utilities as utilities
import discord

client = discord.Client()

utilities.logger.info("Bot in ascolto")

try:
    token = functions.authConfig["token"]
except Exception as ex:
    utilities.logger.error(ex)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


client.run(token)
