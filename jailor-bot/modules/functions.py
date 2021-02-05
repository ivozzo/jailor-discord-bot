from pymongo import MongoClient
from classes.bot_configuration import BotConfiguration
from classes.bot_felony import BotFelony
import modules.configuration as configuration
import modules.utilities as utilities
import datetime

database = None


def create_configuration(guildId):
    previous_bot_configuration = read_configuration(guildId)
    collection = get_configuration_repository()
    if not previous_bot_configuration:
        bot_configuration = BotConfiguration(guildId=guildId)
        utilities.logger.debug(f"Saving configuration {str(bot_configuration)} onto {collection}")
        collection.insert_one(bot_configuration.to_dict())
        return bot_configuration
    else:
        utilities.logger.debug(f"Configuration for {str(guildId)} already existing in {collection}")
        return BotConfiguration.from_dict(previous_bot_configuration)


def update_configuration(guildId, item, value):
    collection = get_configuration_repository()
    return collection.update_many({"guildId": guildId}, {"$set": {item: value}})


def update_felony(guildId, userId, previous_felony_type, reason, new_felony_type):
    collection = get_felony_repository()
    return collection.update_many({"guildId": guildId, "userId": userId, "type": previous_felony_type}, {
        "$set": {"reason": reason, "type": new_felony_type, "timestamp": datetime.datetime.now().timestamp()}})


def read_configuration(guildId):
    collection = get_configuration_repository()
    return collection.find_one({"guildId": guildId})


def remove_configuration(guildId):
    collection = get_configuration_repository()
    return collection.delete_many({"guildId": guildId})


def create_felony(context, user, reason, felony_type):
    collection = get_felony_repository()
    previous_bot_felony = read_felony(context.guild.id, user.id, felony_type.value)
    if not previous_bot_felony:
        bot_felony = BotFelony(guildId=context.guild.id, guildName=context.guild.name, userId=user.id,
                               userName=user.name, type=felony_type.value, reason=reason, authorId=context.author.id,
                               authorName=context.author.name)
        utilities.logger.debug(f"Saving felony {str(bot_felony)} onto {collection}")
        collection.insert_one(bot_felony.to_dict())
        return bot_felony
    else:
        utilities.logger.debug(f"Felony for {str(user.id)} in {str(context.guild.id)} already existing in {collection}")
        return BotFelony.from_dict(previous_bot_felony)


async def read_felonies(guildId, felonyType):
    collection = get_felony_repository()
    configuration = BotConfiguration.from_dict(read_configuration(guildId))
    return collection.find({"guildId": guildId, "type": felonyType,
                            "timestamp": {"$lte": (datetime.datetime.now() - datetime.timedelta(
                                hours=int(configuration.warning_role_timer))).timestamp()}})


def read_felony(guildId, userId, type):
    collection = get_felony_repository()
    return collection.find_one({"guildId": guildId, "userId": userId, "type": type})


async def delete_felony(guildId, userId, type):
    collection = get_felony_repository()
    return collection.delete_many({"guildId": guildId, "userId": userId, "type": type})


def get_felony_repository():
    target_collection = configuration.database["felony_repository"]
    return database[target_collection]


def get_configuration_repository():
    target_collection = configuration.database["configuration_repository"]
    return database[target_collection]


def connect_db(host, user, password, db, port):
    connection_str = host.replace("<username>", user).replace("<password>", password) \
        .replace("<port>", port).replace("<dbname>", db)
    client = MongoClient(connection_str)
    return client[db]


def init_connection():
    global database

    database = connect_db(configuration.database["host"], configuration.database["user"],
                          configuration.database["password"],
                          configuration.database["name"], configuration.database["port"])
