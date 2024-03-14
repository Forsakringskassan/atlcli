import logging

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

