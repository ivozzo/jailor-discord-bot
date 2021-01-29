import logging
import modules.functions as functions

logger = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s|[%(threadName)-12.12s]|[%(levelname)-5.5s]| %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}".format(functions.loggingConfig["path"], functions.loggingConfig["file"])),
        logging.StreamHandler()
    ])

logger = logging.getLogger()