import configparser
from pymongo import MongoClient


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return config


def connect_db(host, user, password, database, port):
    client = MongoClient(
        host.replace("<username>", user).replace("<password>", password).replace("<port>", port).replace("<database>",
                                                                                                         database))
    return client[database]


#def insert_tag(tag):
#    collection = database["tag_repository"]
#    return collection.insert_one(tag.__dict__).inserted_id


#def read_tags(groupId):
#    collection = database["tag_repository"]
#    return collection.find({"group_chat_id": groupId})


config_file = 'config/settings'

config = read_config(config_file)
authConfig = config["auth"]
loggingConfig = config["logging"]
databaseConfig = config["database"]

#database = connect_db(databaseConfig["host"], databaseConfig["user"], databaseConfig["password"],
#                      databaseConfig["name"], databaseConfig["port"])
