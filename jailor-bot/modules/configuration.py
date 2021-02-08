import configparser

logging = {}
database = {}


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return config


def init(config_file):
    global logging
    global database

    config = read_config(config_file)
    logging = config["logging"]
    database = config["database"]
