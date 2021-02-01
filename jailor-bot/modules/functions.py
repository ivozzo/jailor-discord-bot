from pymongo import MongoClient
import modules.configuration as configuration
import modules.utilities as utilities

database = None


def create_configuration(bot_configuration):
    collection = get_configuration_repository()
    utilities.logger.debug(f"Savinf configuration {str(bot_configuration)} onto {collection}")
    return collection.insert_one(bot_configuration.to_dict()).inserted_id


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
    print(connection_str)
    client = MongoClient(connection_str)
    return client[db]


def init_connection():
    global database

    database = connect_db(configuration.database["host"], configuration.database["user"],
                          configuration.database["password"],
                          configuration.database["name"], configuration.database["port"])
