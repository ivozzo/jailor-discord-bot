import sys

from classes.bot_configuration import BotConfiguration
import modules.configuration as configuration
import modules.utilities as utilities
import modules.functions as functions
from classes.bot import JailorBot

client = JailorBot()

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
    utilities.logger.info("Currently deployed on:")
    for guild in client.guilds:
        utilities.logger.info(f"- {guild.name}")
        bot_configuration = functions.read_configuration(guild.id)
        utilities.logger.debug(f"Retrieved configuration: {str(bot_configuration)}")

    utilities.logger.info(f'{client.user} has connected to Discord!')


@client.event
async def on_guild_join(guild):
    utilities.logger.info(f"Jailor has been added to server {guild.name}")
    utilities.logger.debug(f"Creating a brand new default configuration for {guild.id}")
    conf = BotConfiguration(guildId=guild.id)
    functions.create_configuration(conf)

    channel = [x for x in guild.text_channels if "bot" in x.name][0]
    channel = guild.text_channels[0] if not channel else channel

    if channel.permissions_for(guild.me).send_messages:
        utilities.logger.info(f"Writing on channel {channel.name})")
        await channel.send(f"Hey, I'm fresh around here!"
                           f"use the $config command to start configuring me")
    else:
        utilities.logger.info(f"Writing to guild owner {channel.name})")

        user = await client.fetch_user(guild.owner_id)
        await user.send(tts=False, content=f"Hey there fella, I've just joined your server!\n"
                                           f"Give me visibility on a channel and use the $config command to configure me!")


@client.event
async def on_guild_remove(guild):
    utilities.logger.info(f"Jailor has been removed from server {guild.name}")
    utilities.logger.debug(f"Deleting configuration for {guild.id}")
    functions.remove_configuration(guild.id)


utilities.logger.info("Initializing database connection...")
functions.init_connection()

utilities.logger.info("Bot listening...")
client.run(token)
