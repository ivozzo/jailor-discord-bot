
import modules.functions as functions
import modules.utilities as utilities
import classes.configuration as configuration

try:
    token = functions.authConfig["token"]
except Exception as ex:
    utilities.logger.error(ex)

