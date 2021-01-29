import configparser

auth = {}
logging = {}
database = {}


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return config


def init(config_file):
    global auth
    global logging
    global database

    config = read_config(config_file)
    auth = config["auth"]
    logging = config["logging"]
    database = config["database"]
