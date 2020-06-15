from datetime import (
    datetime,
    timedelta
)
import sqlite3

import settings


def get_today_plan_comment(task):
    """Возвращает последний комментарий с планом за сегодняшний день"""
    today = datetime.today().strftime('%Y-%m-%d')
    comments = task.get('comments', [])
    # Разворачиваем список чтобы начать перебор с конца
    comments.reverse()
    for comment in comments:
        if comment.get('text', '').lower().startswith(('plan', 'план')) and today in comment.get('create_date', ''):
            return comment


def get_today_report_comment(task):
    """Возвращает последний комментарий с отчетом за сегодняшний день"""
    today = datetime.today().strftime('%Y-%m-%d')
    comments = task.get('comments', [])
    # Разворачиваем список чтобы начать перебор с конца
    comments.reverse()
    for comment in comments:
        if comment.get('text', '').lower().startswith(('report', 'отчет')) and today in comment.get('create_date', ''):
            return comment


def is_plan_correct(plan, related_tasks):
    '''Проверяет соответствие плана связанным задачам'''
    plan = [subject.lower() for subject in plan.split('\n')]
    # Удаляем слово "План"
    # ['Plan:', 'Пункт плана 1', 'Пункт плана 2'] => ['Пункт плана 1', 'Пункт плана 2']
    plan = plan[1:]
    related_tasks_subjects = [task.get('subject').lower() for task in related_tasks]
    return set(plan) == set(related_tasks_subjects)


def is_report_correct(report, plan):
    '''Проверяет соответствие отчета плану'''
    plan = [subject.lower() for subject in plan.split('\n')]
    # Удаляем слово "Plan"
    # ['Plan:', 'Пункт плана 1', 'Пункт плана 2'] => ['Пункт плана 1', 'Пункт плана 2']
    plan = plan[1:]

    report = [subject.lower() for subject in report.split('\n')]
    # Удаляем слово "Report"
    # ['Report:', 'Пункт отчета 1', 'Пункт отчета 2'] => ['Пункт отчета 1', 'Пункт отчета 2']
    report = report[1:]
    return set(plan) == set(report)


def fetch_user_info(user_email):
    '''Возвращает данные пользователя из базы'''
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {settings.USERS_TABLE_NAME} WHERE email=(?)', (user_email,))
        return cursor.fetchone()


def register_chat_id(email, chat_id):
    '''Сохраняет chat id для telegram-бота'''
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    with conn:
        cursor = conn.cursor()
        sql = f'''UPDATE {settings.USERS_TABLE_NAME}
                 SET chat_id=?
                 WHERE email=?'''
        cursor.execute(sql, (chat_id, email))
        conn.commit()
        return cursor.rowcount


def update_users_table(contacts):
    '''Добавляет все контакты из Pyrus в базу данных'''
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    with conn:
        cursor = conn.cursor()
        sql = f'''SELECT email
                FROM {settings.USERS_TABLE_NAME}'''
        exists_users = cursor.execute(sql).fetchall()
        if exists_users:
            exists_users = [user[0] for user in exists_users]
        new_users = []
        for contact in contacts:
            if contact.get('email') not in exists_users and contact.get('type') != 'bot':
                new_users.append(
                    (
                        int(contact.get('id')),
                        contact.get('email'),
                        contact.get('first_name'),
                        contact.get('last_name'),
                    )
                )
        if new_users:
            sql = f'''INSERT INTO {settings.USERS_TABLE_NAME} (id, email, first_name, last_name)
                    VALUES (?, ?, ?, ?)'''
            cursor.executemany(sql, new_users)
            conn.commit()


def fetch_users_credentials():
    '''Возвращает данные пользователей из базы данных'''
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.cursor()
        sql = f'''SELECT * FROM {settings.USERS_TABLE_NAME}
                WHERE secret_key IS NOT NULL AND
                secret_key != "" AND
                chat_id IS NOT NULL
                '''
        return cursor.execute(sql).fetchall()


def fetch_user_by_id(user_id):
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.cursor()
        sql = f'''SELECT * FROM {settings.USERS_TABLE_NAME}
                WHERE id = ?'''
        return cursor.execute(sql, (user_id, )).fetchone()


def find_task_owner_credentials(task):
    '''Возвращает данные владельца задачи из базы данных'''
    author = task.get('author')
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        sql = f'''SELECT * FROM {settings.USERS_TABLE_NAME}
                WHERE id=(?)'''
        cursor = conn.cursor()
        return cursor.execute(sql, (author.get('id'),)).fetchone()
        

def update_deadline_checking_time(task_id, deadline_time):
    '''Увеличивает счетчик проверок дедлайна на 1 и устанавливает время для следуюущей проверки дедлайна'''
    next_deadline_time = datetime.strptime(deadline_time, "%Y-%m-%d %H:%M:%S%z") + timedelta(minutes=settings.DEADLINE_TIME_STEP)
    conn = sqlite3.connect(settings.DATABASE_FILE_PATH)
    with conn:
        sql = f'''UPDATE {settings.DEADLINES_TABLE_NAME}
                SET deadline_time = ?,
                    checks_number = checks_number + 1
                WHERE id = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (next_deadline_time.strftime("%Y-%m-%d %H:%M:%S%z"), task_id))
