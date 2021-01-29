import modules.functions as functions
import modules.utilities as utilities

try:
    token = functions.auth["token"]
except Exception as ex:
    utilities.logger.error(ex)
