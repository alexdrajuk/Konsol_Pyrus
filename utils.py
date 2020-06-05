import re
from datetime import (
    datetime,
    timedelta,
)

import pytz

from settings import DEADLINE_TIME_TRESHOLD


def extract_deadline_date(task_title):
    deadline_date = re.findall(r'\d{8}', task_title)
    if deadline_date:
        deadline_date = deadline_date[0].strip()
        year = deadline_date[4:]
        month = deadline_date[2:4]
        day = deadline_date[:2]
        # According to Pyrus' time format
        # https://pyrus.com/ru/help/api/tasks#addcomment
        return f'{year}-{month}-{day}'


def extract_deadline_time(task_title):
    deadline_time = re.findall(r'\s(\d{4})$', task_title)
    if deadline_time:
        deadline_time = deadline_time[0].strip()
        hours, minutes = deadline_time[:2], deadline_time[2:]
        # According to Pyrus' time format
        # https://pyrus.com/ru/help/api/tasks#addcomment
        return f'T{hours}:{minutes}:00Z'


def extract_task_title(task_title):
    if not re.findall(r'\d{8}', task_title):
        return task_title
    title = re.findall(r'^(.*)\s\d{8}', task_title)
    if title:
        return title[0].strip()


def utc_to_localtime(utc_time):
    local_tz = pytz.timezone('Europe/Kiev')
    return utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)


def get_deadline_time(task):
    if task.get('due_date'):
        deadline_time = datetime.strptime(task.get('due_date'), '%Y-%m-%d')
        return utc_to_localtime(deadline_time)
    elif task.get('due'):
        deadline_time = datetime.strptime(task.get('due'), '%Y-%m-%dT%H:%M:%SZ')
        return utc_to_localtime(deadline_time)
    return None


def is_deadline_come(deadline_time, treshold=DEADLINE_TIME_TRESHOLD):
    '''
    Сравнивает текущее время с временем дедлайна задачи. Возращает True или False

    Args:
        deadline_time(str):
            Время дедлайна

        treshold(int):
            Определяет допустимую разницу в минутах между текущим временем и временем дедлайна при которой будет отправлено сообщение о наступлении дедлайна
            Например: дедлайн задачи в 12:00 а скрипт проверил задачу в 11:57, то сообщение о дедлайне будет отправлено (12:00 - 11:57 = 3мин)
            Если же дедлайн задачи в 12:00 а скрипт проверил задачу в 11:52, то сообщение о дедлайне НЕ будет отправлено (12:00 - 11:52 = 8мин)

    Returns:
        (bool)
    '''
    tz = pytz.timezone('Europe/Kiev')
    now = datetime.now(tz=tz)
    deadline_time = datetime.strptime(deadline_time, "%Y-%m-%d %H:%M:%S%z")
    diff_in_minutes = divmod(abs((now - deadline_time)).total_seconds(), 60)[0]
    return diff_in_minutes < treshold
