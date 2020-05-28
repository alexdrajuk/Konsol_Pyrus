import re


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
