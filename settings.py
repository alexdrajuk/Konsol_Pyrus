import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_FILE_PATH = os.getenv('DATABASE_FILE_PATH')
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')
DEADLINES_TABLE_NAME = os.getenv('DEADLINES_TABLE_NAME')

# Telegram-bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Notification messages
#######################

# Сообщение о пустом списке "План" (для владельца задачи)
EMPTY_PLAN_LIST_MESSAGE_FOR_OWNER = 'Cписок "План" пуст у разработчика {developer_name}'

# Сообщение о пустом списке "План" (для разработчика)
EMPTY_PLAN_LIST_MESSAGE_FOR_DEV = 'Предупреждение о штрафе. Заполните план'

# Сообщение об отсутствии плана в задаче (для владельца задачи)
EMPTY_PLAN_TASK_MESSAGE_FOR_OWNER = 'Отсутсвует план для задачи:\n{task_subject}\n{task_link}\nУ разработчика {developer_name}'

# Сообщение об отсутствии плана в задаче (для разработчика)
EMPTY_PLAN_TASK_MESSAGE_FOR_DEV = 'Предупреждение о штрафе. Заполните план для задачи:\n{task_subject}\n{task_link}'

# Сообщение о неправильном плане в задаче (для разработчика)
INCORRECT_PLAN_TASK_MESSAGE_FOR_DEV = 'План для задачи:\n{task_subject} не соответствует подзадачам\n{task_link}'

# Сообщение о пустом отчете (для владельца задачи)
EMPTY_REPORT_MESSAGE_FOR_OWNER = 'Отсутствует отчет по задаче: {task_subject}\n{task_link}'

# Сообщение о пустом отчете (для разработчика)
EMPTY_REPORT_MESSAGE_FOR_DEV = 'Предупреждение о штрафе. Выполните задачу:\n{task_subject}\n{task_link}'

# Сообщение о штрафе за отсутствие плана
EMPTY_PLAN_FINE_MESSAGE = 'Штраф за отсутствие плана для задачи:\n{task_subject}\n{task_link}\n{current_date}'

# Сообщение о штрафе за отсутвие отчета
EMPTY_REPORT_FINE_MESSAGE = 'Штраф за отсутствие отчета для задачи:\n{task_subject}\n{task_link}\n{current_date}'


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
