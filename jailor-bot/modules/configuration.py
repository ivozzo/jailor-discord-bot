import configparser
import os

from dotenv import load_dotenv

config_file = "jailor-bot/config/settings"

logging = {}
database = {}

load_dotenv()
token = os.getenv("JAILOR_DISCORD_TOKEN")
logging_level = os.getenv("JAILOR_LOGGING_LEVEL")
user = os.getenv("JAILOR_DATABASE_USER")
password = os.getenv("JAILOR_DATABASE_PASSWORD")
db_name = os.getenv("JAILOR_DATABASE")
host = os.getenv("JAILOR_DATABASE_HOST")


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return config


def init():
    global logging
    global database

    config = read_config(config_file)
    logging = config["logging"]
    database = config["database"]
