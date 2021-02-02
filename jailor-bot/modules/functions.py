from pymongo import MongoClient
from classes.bot_configuration import BotConfiguration
import modules.configuration as configuration
import modules.utilities as utilities

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

def read_configuration(guildId):
    collection = get_configuration_repository()
    return collection.find_one({"guildId": guildId})


def remove_configuration(guildId):
    collection = get_configuration_repository()
    return collection.delete_many({"guildId": guildId})


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
