import modules.functions as functions
import modules.utilities as utilities

try:
    token = functions.authConfig["token"]
except Exception as ex:
    utilities.logger.error(ex)
