import asyncio
import sys
import os
from dotenv import load_dotenv

import modules.configuration as configuration
import modules.functions as functions
import modules.utilities as utilities
from classes.bot import JailorBot
from enums.felony_type import FelonyType

client = JailorBot()

load_dotenv()
token = os.getenv("JAILOR_DISCORD_TOKEN")
logging_level = os.getenv("JAILOR_LOGGING_LEVEL")

try:
    configuration.init("jailor-bot/config/settings")
    utilities.init_logger(logging_level)
except Exception as ex:
    utilities.logger.error(ex)

utilities.logger.debug(f'Number of arguments: {len(sys.argv)} arguments.')
utilities.logger.debug(f'Argument List: {str(sys.argv)}')


@client.event
async def on_ready():
    utilities.logger.info(f'{client.user} has connected to Discord!')
    client.loop.create_task(check_warning_task())
    client.loop.create_task(check_muted_task())


async def check_warning_task():
    while True:
        for guild in client.guilds:
            utilities.logger.debug(f"Searching WARNING felonies for guild {guild.id}")
            felonies = list(await functions.read_felonies(guild.id, FelonyType.WARNING.value))
            utilities.logger.debug(f"Got these WARNING {felonies}")
            if len(felonies) > 0:
                await client.remove_felony(guild=guild, felonies=list(felonies), felony_type=FelonyType.WARNING.value)
        await asyncio.sleep(600)


async def check_muted_task():
    while True:
        for guild in client.guilds:
            utilities.logger.debug(f"Searching MUTE felonies for guild {guild.id}")
            felonies = list(await functions.read_felonies(guild.id, FelonyType.MUTE.value))
            utilities.logger.debug(f"Got these MUTE {felonies}")
            if len(felonies) > 0:
                await client.remove_felony(guild=guild, felonies=list(felonies), felony_type=FelonyType.MUTE.value)
        await asyncio.sleep(600)


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
functions.init_connection(user=os.getenv("JAILOR_DATABASE_USER"), password=os.getenv("JAILOR_DATABASE_PASSWORD"),
                          db_name=os.getenv("JAILOR_DATABASE"), host=os.getenv("JAILOR_DATABASE_HOST"))

client.run(token)
