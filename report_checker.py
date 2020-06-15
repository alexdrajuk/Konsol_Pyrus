import time
import logging.config
from datetime import datetime

import lib
import utils
from pyrus import PyrusAccount
from messenger import Messenger

import schedule
import settings

logging.config.dictConfig(settings.logger_config)
logger = logging.getLogger('app_logger')

Messenger = Messenger(settings.TELEGRAM_BOT_TOKEN)


def check_users_reports(empty_report_fine_message=False, notify_manager=True):
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
                Messenger.send_message(credentials.get('chat_id'), settings.EMPTY_PLAN_LIST_MESSAGE_FOR_DEV)
                continue
            for task in planed_tasks:
                task_id, task_subject = task.get('id'), task.get('subject')
                assignee_chat_id = credentials.get('chat_id')
                owner_chat_id = dict(lib.find_task_owner_credentials(task)).get('chat_id')
                report_comment = lib.get_today_report_comment(task)
                # Отправляем уведомление
                # Если в задаче не указан отчет (нет ни одного комментария начинающегося строкой "Отчет")
                if not report_comment:
                    Messenger.send_message(
                        assignee_chat_id,
                        settings.EMPTY_REPORT_MESSAGE_FOR_DEV.format(
                            task_subject=task_subject,
                            task_link=utils.generate_task_link(task_id)
                        )
                    )
                    # Если параметр notify_manager равен True,
                    # И chat_id владельца вдадельца не равен chat_id ответственного по задаче то также отправляем уведомление владельцу (автору) задачи
                    if notify_manager and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(
                            owner_chat_id,
                            settings.EMPTY_REPORT_MESSAGE_FOR_OWNER.format(
                                task_subject=task_subject,
                                task_link=utils.generate_task_link(task_id),
                                developer_name=f"{credentials.get('first_name')} {credentials.get('last_name')}"
                            )
                        )
                    elif empty_report_fine_message and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(
                            owner_chat_id,
                            settings.EMPTY_REPORT_FINE_MESSAGE.format(
                                task_subject=task_subject,
                                task_link=utils.generate_task_link(task_id),
                                current_date=datetime.now().strftime('%d.%m.%Y')
                            )
                        )
                if not lib.is_report_correct(report_comment.get('text', ''), account.fetch_related_tasks(task)):
                    Messenger.send_message(
                        assignee_chat_id,
                        settings.INCORRECT_REPORT_TASK_MESSAGE_FOR_DEV.format(
                            task_subject=task_subject,
                            task_link=utils.generate_task_link(task_id)
                        )
                    )
        except Exception:
            logger.debug('Something went wrong', exc_info=True)
            continue


schedule.every().monday.at('19:00').do(check_users_reports)
schedule.every().monday.at('19:10').do(check_users_reports)
schedule.every().monday.at('19:20').do(check_users_reports)
schedule.every().monday.at('19:30').do(check_users_reports, empty_report_fine_message=False)
schedule.every().tuesday.at('19:00').do(check_users_reports)
schedule.every().tuesday.at('19:10').do(check_users_reports)
schedule.every().tuesday.at('19:20').do(check_users_reports)
schedule.every().tuesday.at('19:30').do(check_users_reports, empty_report_fine_message=False)
schedule.every().wednesday.at('19:00').do(check_users_reports)
schedule.every().wednesday.at('19:10').do(check_users_reports)
schedule.every().wednesday.at('19:20').do(check_users_reports)
schedule.every().wednesday.at('19:30').do(check_users_reports, empty_report_fine_message=False)
schedule.every().thursday.at('19:00').do(check_users_reports)
schedule.every().thursday.at('19:10').do(check_users_reports)
schedule.every().thursday.at('19:20').do(check_users_reports)
schedule.every().thursday.at('19:30').do(check_users_reports, empty_report_fine_message=False)
schedule.every().friday.at('19:00').do(check_users_reports)
schedule.every().friday.at('19:10').do(check_users_reports)
schedule.every().friday.at('19:20').do(check_users_reports)
schedule.every().friday.at('19:30').do(check_users_reports, empty_report_fine_message=False)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(60)
