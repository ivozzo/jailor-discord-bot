import asyncio
import sys

import modules.configuration as configuration
import modules.functions as functions
import modules.utilities as utilities
from classes.bot import JailorBot
from enums.felony_type import FelonyType

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
    utilities.logger.info(f'{client.user} has connected to Discord!')
    client.loop.create_task(check_warning_task())


async def check_warning_task():
    while True:
        for guild in client.guilds:
            utilities.logger.debug(f"Searching WARNING felonies for guild {guild.id}")
            felonies = list(await functions.read_felonies(guild.id, FelonyType.WARNING.value))
            utilities.logger.debug(f"Got these WARNING {felonies}")
            if len(felonies) > 0:
                await client.remove_felony(guild=guild, felonies=list(felonies), felony_type=FelonyType.WARNING.value)
        await asyncio.sleep(10)


@client.event
async def on_guild_join(guild):
    utilities.logger.info(f"Jailor has been added to server {guild.name}")
    utilities.logger.debug(f"Creating a brand new default configuration for {guild.id}")
    conf = functions.create_configuration(guildId=guild.id)

    user = await client.fetch_user(guild.owner_id)
    utilities.logger.info(f"Writing to guild owner {user.name}")
    await user.send(tts=False, content=f"Hey there fella, I've just joined your server!\n"
                                       f"Give me visibility on a channel and use the \"{conf.command_prefix}"
                                       f" config\" command to start configuring me!")


@client.event
async def on_guild_remove(guild):
    utilities.logger.info(f"Jailor has been removed from server {guild.name}")
    utilities.logger.debug(f"Deleting configuration for {guild.id}")
    functions.remove_configuration(guild.id)


utilities.logger.info("Initializing database connection...")
functions.init_connection()

client.run(token)
