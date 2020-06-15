import time
import logging.config
from datetime import datetime

import schedule

import settings
import lib
import utils
from pyrus import PyrusAccount
from messenger import Messenger


logging.config.dictConfig(settings.logger_config)
logger = logging.getLogger('app_logger')

Messenger = Messenger(settings.TELEGRAM_BOT_TOKEN)


def check_users_plans(empty_plan_fine_message=False, notify_manager=True):
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
                plan_comment = lib.get_today_plan_comment(task)
                # Отправляем уведомление
                # Если в задаче не указан план (нет ни одного комментария начинающегося строкой "План")
                if not plan_comment:
                    Messenger.send_message(
                        assignee_chat_id,
                        settings.EMPTY_PLAN_TASK_MESSAGE_FOR_DEV.format(
                            task_subject=task_subject,
                            task_link=utils.generate_task_link(task_id)
                        )
                    )
                    # Если параметр notify_manager равен True,
                    # И chat_id владельца вдадельца не равен chat_id ответственного по задаче то также отправляем уведомление владельцу (автору) задачи
                    if notify_manager and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(
                            owner_chat_id,
                            settings.EMPTY_PLAN_TASK_MESSAGE_FOR_OWNER.format(
                                task_subject=task_subject,
                                task_link=utils.generate_task_link(task_id),
                                developer_name=f"{credentials.get('first_name')} {credentials.get('last_name')}"
                            )
                        )
                    elif empty_plan_fine_message and assignee_chat_id != owner_chat_id:
                        Messenger.send_message(
                            owner_chat_id,
                            settings.EMPTY_PLAN_FINE_MESSAGE.format(
                                task_subject=task_subject,
                                task_link=utils.generate_task_link(task_id),
                                current_date=datetime.now().strftime('%d.%m.%Y')
                            )
                        )

                if not lib.is_plan_correct(plan_comment.get('text', ''), account.fetch_related_tasks(task)):
                    Messenger.send_message(
                        assignee_chat_id,
                        settings.INCORRECT_PLAN_TASK_MESSAGE_FOR_DEV.format(
                            task_subject=task_subject,
                            task_link=utils.generate_task_link(task_id)
                        )
                    )
        except Exception:
            logger.debug('Something went wrong', exc_info=True)
            continue


schedule.every().monday.at('11:00').do(check_users_plans)
schedule.every().monday.at('11:10').do(check_users_plans)
schedule.every().monday.at('11:20').do(check_users_plans)
schedule.every().monday.at('11:30').do(check_users_plans, empty_plan_fine_message=True)
schedule.every().tuesday.at('11:00').do(check_users_plans)
schedule.every().tuesday.at('11:10').do(check_users_plans)
schedule.every().tuesday.at('11:20').do(check_users_plans)
schedule.every().tuesday.at('11:30').do(check_users_plans, empty_plan_fine_message=True)
schedule.every().wednesday.at('11:00').do(check_users_plans)
schedule.every().wednesday.at('11:10').do(check_users_plans)
schedule.every().wednesday.at('11:20').do(check_users_plans)
schedule.every().wednesday.at('11:30').do(check_users_plans, empty_plan_fine_message=True)
schedule.every().thursday.at('11:00').do(check_users_plans)
schedule.every().thursday.at('11:10').do(check_users_plans)
schedule.every().thursday.at('11:20').do(check_users_plans)
schedule.every().thursday.at('11:30').do(check_users_plans, empty_plan_fine_message=True)
schedule.every().friday.at('11:00').do(check_users_plans)
schedule.every().friday.at('11:10').do(check_users_plans)
schedule.every().friday.at('11:20').do(check_users_plans)
schedule.every().friday.at('11:30').do(check_users_plans, empty_plan_fine_message=True)


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(60)
