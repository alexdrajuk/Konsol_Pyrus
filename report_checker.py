import time
import logging.config

from pyrus import PyrusAccount
import lib
from messenger import Messenger

import schedule
import settings

logging.config.dictConfig(settings.logger_config)
logger = logging.getLogger('app_logger')

Messenger = Messenger(settings.TELEGRAM_BOT_TOKEN)


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
                if not lib.is_report_correct(report_comment.get('text', ''), account.fetch_related_tasks(task)):
                    Messenger.send_message(
                        assignee_chat_id,
                        incorrect_report_task_message.format(task_name=task.get('subject'), task_id=task.get('id'))
                    )
        except Exception:
            logger.debug('Something went wrong', exc_info=True)
            continue


schedule.every().monday.at('19:00').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().monday.at('19:10').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().monday.at('19:20').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().monday.at('19:30').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    notify_manager=True,
)


schedule.every().tuesday.at('19:00').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().tuesday.at('19:10').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().tuesday.at('19:20').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().tuesday.at('19:30').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    notify_manager=True,
)

schedule.every().wednesday.at('19:00').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().wednesday.at('19:10').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().wednesday.at('19:20').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().wednesday.at('19:30').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    notify_manager=True,
)

schedule.every().thursday.at('19:00').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().thursday.at('19:10').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().thursday.at('19:20').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().thursday.at('19:30').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении ',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    notify_manager=True,
)

schedule.every().friday.at('19:00').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().friday.at('19:10').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().friday.at('19:20').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Предупреждение о штрафе',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
)

schedule.every().friday.at('19:30').do(
    check_users_reports,
    empty_plan_list_message='Ваш список "План" пуст. Руководство знает о невыполнении',
    empty_report_task_message='Отсутствует отчет для задачи {task_name} \nhttps://pyrus.com/t#{task_id}',
    incorrect_report_task_message='Отчет для задачи {task_name} не соответствует подзадачам \nhttps://pyrus.com/t#{task_id}',
    notify_manager=True,
)


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(60)
