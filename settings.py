import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_FILE_PATH = os.getenv('DATABASE_FILE_PATH')
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')

# Telegram-bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Logging settings
logger_config = {
    'version': 1,
    'disble_existing_loggers': False,
    'formatters': {
        'std_format': {
            'format': '{asctime} - {levelname} - {name} - {message}',
            'style': '{'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs.log',
            'mode': 'a',
            'formatter': 'std_format',
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    }
}
