import logging
import os
import coloredlogs

COLOREDLOGS_LOG_FORMAT = 'COLOREDLOGS_LOG_FORMAT'
LOG_FORMAT = '%(asctime)-15s %(levelname)-7s %(module)s %(message)s'

LOG_LEVELS = ['error', 'warning', 'info', 'debug']
nameToLevel = {
    # Converts logging level command line values to logging levels
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}

def install_colored_logs(loglevel):
    if COLOREDLOGS_LOG_FORMAT in os.environ is None:
        coloredlogs.install(level=nameToLevel[loglevel])
    else:
        coloredlogs.install(level=nameToLevel[loglevel], fmt=LOG_FORMAT)