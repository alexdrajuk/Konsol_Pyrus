import os
import time
import logging.config

from pyrus import PyrusAccount
import lib
from messenger import Messenger

import schedule
from settings import (
    TELEGRAM_BOT_TOKEN,
    logger_config
)

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

# account = PyrusAccount(os.getenv('ADMIN_LOGIN'), os.getenv('ADMIN_SECRET_KEY'))
Messenger = Messenger(TELEGRAM_BOT_TOKEN)


def check_users_plans(empty_plan_list_message, empty_plan_task_message, incorrect_plan_task_message, notify_manager=False):
    # Достаем из базы всех пользователей у которых есть secret_key для API Pyrus
    users_credentials = lib.fetch_users_credentials()
    for credentials in users_credentials:
        credentials = dict(credentials)
        try:
            # Для каждого пользователя создаем экземпляр класса PyrusAccount для работы с API
            account = PyrusAccount(credentials.get('email'), credentials.get('secret_key'))
            # Получаем все задачи из списка "Plan"
            planed_tasks = account.get_planed_tasks()
            # Отправляем уведомление если в списке "Plan" нет ни одной задачи
            if not planed_tasks:
                Messenger.send_message(credentials.get('chat_id'), empty_plan_list_message)
                continue
            for task in planed_tasks:
                assignee_chat_id = credentials.get('chat_id')
                owner_chat_id = dict(lib.find_task_owner_credentials(task)).get('chat_id')
                plan_comment = lib.get_today_plan_comment(task)
                # Отправляем уведомление
                # Если в задаче не указан план (нет ни одного комментария начинающегося строкой "План")
                if not plan_comment:
                    message = empty_plan_task_message.format(task_name=task.get('subject'), task_id=task.get('id'))
                    Messenger.send_message(assignee_chat_id, message)
                    # Если параметр notify_manager равен True,
                    # И chat_id владельца вдадельца не равен chat_id ответственного по задаче то также отправляем уведомление владельцу (автору) задачи
                    if notify_manager and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(owner_chat_id, message)
                if not lib.is_plan_correct(plan_comment.get('text', ''), account.fetch_related_tasks(task)):
                    Messenger.send_message(
                        assignee_chat_id,
                        incorrect_plan_task_message.format(task_name=task.get('subject'), task_id=task.get('id'))
                    )
        except Exception:
            logger.debug('Something went wrong', exc_info=True)
            continue


def check_users_reports(empty_plan_list_message, empty_report_task_message, incorrect_report_task_message, notify_manager=False):
    # Достаем из базы всех пользователей у которых есть secret_key для API Pyrus
    users_credentials = lib.fetch_users_credentials()
    for credentials in users_credentials:
        credentials = dict(credentials)
        try:
            # Для каждого пользователя создаем экземпляр класса PyrusAccount для работы с API
            account = PyrusAccount(credentials.get('email'), credentials.get('secret_key'))
            # Получаем все задачи из списка "Plan"
            planed_tasks = account.get_planed_tasks()
            # Отправляем уведомление если в списке "Plan" нет ни одной задачи
            if not planed_tasks:
                Messenger.send_message(credentials.get('chat_id'), empty_plan_list_message)
                continue
            for task in planed_tasks:
                assignee_chat_id = credentials.get('chat_id')
                owner_chat_id = dict(lib.find_task_owner_credentials(task)).get('chat_id')
                report_comment = lib.get_today_report_comment(task)
                # Отправляем уведомление
                # Если в задаче не указан отчет (нет ни одного комментария начинающегося строкой "Отчет")
                if not report_comment:
                    message = empty_report_task_message.format(task_name=task.get('subject'), task_id=task.get('id'))
                    Messenger.send_message(assignee_chat_id, message)
                    # Если параметр notify_manager равен True,
                    # И chat_id владельца вдадельца не равен chat_id ответственного по задаче то также отправляем уведомление владельцу (автору) задачи
                    if notify_manager and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(owner_chat_id, message)
                    continue
                if not lib.is_report_correct(report_comment.get('text', ''), account.fetch_related_tasks(task)):
                    Messenger.send_message(
                        assignee_chat_id,
                        incorrect_report_task_message.format(task_name=task.get('subject'), task_id=task.get('id'))
                    )
        except Exception:
            logger.debug('', exc_info=True)
            continue


def clear_plans():
    user_credentials = lib.fetch_users_credentials()
    for credentials in user_credentials:
        credentials = dict(credentials)
        try:
            account = PyrusAccount(credentials.get('email'), credentials.get('secret_key'))
            account.clear_plan_list()
        except Exception:
            logger.debug('Something went wrong during clear_plans', exc_info=True)

schedule.every().monday.at("23:00").do(clear_plans)
schedule.every().tuesday.at("23:00").do(clear_plans)
schedule.every().wednesday.at("23:00").do(clear_plans)
schedule.every().thursday.at("23:00").do(clear_plans)
schedule.every().friday.at("23:00").do(clear_plans)

schedule.every().monday.at('11:00').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:10').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:20').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:30').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
        notify_manager=True,
    )
)


schedule.every().tuesday.at('11:00').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:10').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:20').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:30').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
        notify_manager=True,
    )
)

schedule.every().wednesday.at('11:00').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:10').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:20').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:30').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
        notify_manager=True,
    )
)

schedule.every().thursday.at('11:00').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:10').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:20').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:30').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
        notify_manager=True,
    )
)

schedule.every().friday.at('11:00').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:10').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:20').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:30').do(
    check_users_plans(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_plan_task_message='Отсутствует план для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_plan_task_message='План для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
        notify_manager=True,
    )
)

# ################
# Проверка отчетов
# ################

schedule.every().monday.at('11:00').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:10').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:20').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().monday.at('11:30').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:00').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:10').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:20').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().tuesday.at('11:30').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:00').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:10').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:20').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().wednesday.at('11:30').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:00').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:10').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:20').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().thursday.at('11:30').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:00').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:10').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:20').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

schedule.every().friday.at('11:30').do(
    check_users_reports(
        empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
        empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
        incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    )
)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
