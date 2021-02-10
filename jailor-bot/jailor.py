import asyncio

from boilerplate.logger import Logger

import modules.configuration as configuration
from classes.bot import JailorBot
from classes.database import JailorDatabase
from enums.felony_type import FelonyType

logger = None
database = None

if configuration.logging_level:
    logger = Logger(level=configuration.logging_level)
else:
    raise Exception("Environment variable JAILOR_LOGGING_LEVEL not found")

configuration.init()
try:
    database = JailorDatabase(host=configuration.host, user=configuration.user,
                              database=configuration.database, password=configuration.password,
                              felony_repository=configuration.database["felony_repository"],
                              configuration_repository=configuration.database["configuration_repository"],
                              logger=logger)
except Exception as ex:
    logger.error(ex)

client = JailorBot(database=database, logger=logger)


@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')
    client.loop.create_task(check_warning_task())
    client.loop.create_task(check_muted_task())


async def check_warning_task():
    while True:
        for guild in client.guilds:
            logger.debug(f"Searching WARNING felonies for guild {guild.id}")
            felonies = list(await database.read_felonies(guild_id=guild.id, felony_type=FelonyType.WARNING.value))
            logger.debug(f"Got these WARNING {felonies}")
            if len(felonies) > 0:
                await client.remove_felony(guild=guild, felonies=list(felonies), felony_type=FelonyType.WARNING.value)
        await asyncio.sleep(600)


async def check_muted_task():
    while True:
        for guild in client.guilds:
            logger.debug(f"Searching MUTE felonies for guild {guild.id}")
            felonies = list(await database.read_felonies(guild_id=guild.id, felony_type=FelonyType.MUTE.value))
            logger.debug(f"Got these MUTE {felonies}")
            if len(felonies) > 0:
                await client.remove_felony(guild=guild, felonies=list(felonies), felony_type=FelonyType.MUTE.value)
        await asyncio.sleep(600)


@client.event
async def on_guild_join(guild):
    logger.info(f"Jailor has been added to server {guild.name}")
    logger.info(f"Creating a brand new default configuration for {guild.name} - {guild.id}")
    conf = database.create_configuration(guild_id=guild.id)

    user = await client.fetch_user(guild.owner_id)
    logger.info(f"Writing to guild owner {user.name}")
    await user.send(tts=False, content=f"Hey there fella, I've just joined your server!\n"
                                       f"Give me visibility on a channel and use the \"{conf.command_prefix}"
                                       f" config\" command to start configuring me!")


@client.event
async def on_guild_remove(guild):
    logger.info(f"Jailor has been removed from server {guild.name}")
    logger.info(f"Deleting configuration for  {guild.name} - {guild.id}")
    database.remove_configuration(guild_id=guild.id)


logger.info("Initializing database connection...")

client.run(configuration.token)
