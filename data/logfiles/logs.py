import logging.config
import os

path = os.getcwd()
name_file = os.path.join(path, 'data', 'logfiles', 'logs.txt')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '%(levelname)s:%(asctime)s\n %(message)s\n',
            'datefmt': '%d-%m-%y %H:%M:%S'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': name_file,
            'maxBytes': 15360,
            'backupCount': 1,
            'encoding': 'utf-8',
            'formatter': 'default_formatter'
        },
    },

    'loggers': {
        'my_logger': {
            'handlers': ['stream_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('my_logger')
