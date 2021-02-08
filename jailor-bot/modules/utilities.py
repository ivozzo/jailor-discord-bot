import logging

import modules.configuration as configuration

logger = None


def init_logger(logging_level):
    global logger

    loggerDictionary = {"INFO": logging.INFO, "WARN": logging.WARN, "DEBUG": logging.DEBUG, "ERROR": logging.ERROR}

    logging.basicConfig(
        level=loggerDictionary[logging_level],
        format="%(asctime)s|[%(threadName)-12.12s]|[%(levelname)-5.5s]| %(message)s",
        handlers=[
            logging.FileHandler("{0}/{1}".format(configuration.logging["path"], configuration.logging["file"])),
            logging.StreamHandler()
        ])

    logger = logging.getLogger()
