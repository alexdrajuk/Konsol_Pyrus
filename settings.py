import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_FILE_PATH = os.getenv('DATABASE_FILE_PATH')
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')
DEADLINES_TABLE_NAME = os.getenv('DEADLINES_TABLE_NAME')

# Telegram-bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Options
#########

# Определяет допустимую разницу в минутах
# между текущим временем и дедлайном при которой будет отправлено сообщение о наступлении дедлайна

# Например: DEADLINE_TIME_TRESHOLD = 5
# дедлайн задачи в 12:00 а скрипт проверил задачу в 11:57, то сообщение о дедлайне будет отправлено (12:00 - 11:57 = 3мин )
# (3мин < 5мин)

# Если же дедлайн задачи в 12:00 а скрипт проверил задачу в 11:52, то сообщение о дедлайне НЕ будет отправлено (12:00 - 11:52 = 8мин)
# (8мин < 5мин)
DEADLINE_TIME_TRESHOLD = 5

# Определяем время в минутах для повторной проверки делайна
# Например: DEADLINE_TIME_STEP = 10 и время дедлайна равно 12:45
# Если скрипт проверил время дедлайна и задача еще не выполнена то следующая проверка пройдет ~ в 12:55
DEADLINE_TIME_STEP = 10

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
