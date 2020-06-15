import time
import sqlite3
import logging.config

import lib
import utils
import settings
from pyrus import PyrusAccount
from messenger import Messenger

import schedule

logging.config.dictConfig(settings.logger_config)
logger = logging.getLogger('app_logger')

messenger = Messenger(settings.TELEGRAM_BOT_TOKEN)


def collect_deadlines():
    '''Проходит по задачам из списков "Входящие" и "Plan" и сохраняет время дедлайнов в базу данных.'''
    users_credentials = lib.fetch_users_credentials()
    for credentials in users_credentials:
        credentials = dict(credentials)
        try:
            account = PyrusAccount(credentials.get('email'), credentials.get('secret_key'))

            tasks = [account.get_task(task.get('id')) for task in account.get_inbox()]
            tasks.extend(account.get_task(task.get('id')) for task in account.get_planed_tasks())
            deadlines_info = [
                (
                    task.get('id'),
                    task.get('author').get('id'),
                    task.get('responsible').get('id'),
                    utils.get_deadline_time(task),
                    int(utils.is_task_closed(task))  # (int) For compatibility with SQLite DB
                ) for task in tasks
            ]

            conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
            with conn:
                sql = f'''REPLACE INTO {settings.DEADLINES_TABLE_NAME}
                        (id, author_id, responsible_id, deadline_time, is_task_closed)
                        VALUES (?, ?, ?, ?, ?)'''
                cursor = conn.cursor()
                cursor.executemany(sql, deadlines_info)
        except Exception:
            logger.debug('Something went wrong in collect_deadlines', exc_info=True)
            continue


def remind_about_deadlines():
    '''Проходит по дедлайнам из базы данных и отправляет оповещение о наступившем дедлайне'''
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        sql = f'''SELECT u.id as responsible_id,
                u.chat_id as user_chat_id,
                d.id as task_id,
                d.author_id,
                d.deadline_time,
                d.checks_number
                from {settings.USERS_TABLE_NAME} u
                INNER JOIN {settings.DEADLINES_TABLE_NAME} d ON
                u.id = d.responsible_id
                WHERE d.deadline_time is not NULL AND
                d.is_task_closed != 1 AND d.checks_number <= 3'''
        cursor = conn.cursor()
        deadlines = cursor.execute(sql).fetchall()

    for deadline in deadlines:
        deadline = dict(deadline)
        task_id, deadline_time = deadline.get('task_id'), deadline.get('deadline_time')
        if utils.is_deadline_come(deadline_time):
            checks_number = deadline.get('checks_number')
            if checks_number < 2:
                messenger.send_message(
                    deadline.get('user_chat_id'),
                    f"Время дедлайна для задачи\n{utils.generate_task_link(task_id)}"
                )
            if checks_number == 2:
                messenger.send_message(
                    deadline.get('user_chat_id'),
                    f"Время дедлайна для задачи\n{utils.generate_task_link(task_id)}\nОповещение о штрафе"
                )
            if checks_number == 3:
                messenger.send_message(
                    deadline.get('user_chat_id'),
                    f"Время дедлайна для задачи\n{utils.generate_task_link(task_id)}\nОповещение для руководства"
                )
                # Если владелец таски и исполнитель НЕ ОДНО И ТО ЖЕ ЛИЦО, то также уведомляем владельца таски
                if deadline.get('author_id') != deadline.get('responsible_id'):
                    manager_id = lib.fetch_user_by_id(deadline.get('author_id')).get('chat_id')
                    messenger.send_message(
                        manager_id,
                        f"Время дедлайна для задачи\n{utils.generate_task_link(task_id)}\nОповещение для руководства"
                    )
            lib.update_deadline_checking_time(task_id, deadline_time)


schedule.every().monday.at("12:00").do(collect_deadlines)
schedule.every().monday.at("16:00").do(collect_deadlines)

schedule.every().tuesday.at("12:00").do(collect_deadlines)
schedule.every().tuesday.at("16:00").do(collect_deadlines)

schedule.every().wednesday.at("12:00").do(collect_deadlines)
schedule.every().wednesday.at("16:00").do(collect_deadlines)

schedule.every().thursday.at("12:00").do(collect_deadlines)
schedule.every().thursday.at("16:00").do(collect_deadlines)

schedule.every().friday.at("12:00").do(collect_deadlines)
schedule.every().friday.at("16:00").do(collect_deadlines)


schedule.every(5).minutes.do(remind_about_deadlines)


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(60)
