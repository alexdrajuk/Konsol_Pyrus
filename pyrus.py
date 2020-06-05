import logging

import requests

from decorators import http_error_decorator

logger = logging.getLogger('app_logger')


class PyrusAccount:

    @http_error_decorator
    def __init__(self, login, secret_key):
        url = 'https://api.pyrus.com/v4/auth'
        params = {
            'login': login,
            'security_key': secret_key,
        }
        response = requests.get(url, params=params)
        response_data = response.json()
        response.raise_for_status()
        self.token = response_data.get('access_token')

    @http_error_decorator
    def get_task(self, task_id):
        url = f"https://api.pyrus.com/v4/tasks/{task_id}"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        task = response_data.get('task')
        return task

    @http_error_decorator
    def get_lists(self):
        url = "https://api.pyrus.com/v4/lists"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        lists = response_data.get('lists')
        return lists

    @http_error_decorator
    def get_planed_tasks(self):
        '''Возвращает все задачи из списка "Plan"'''
        plan_list_id = None
        for lst in self.get_lists():
            if lst.get('name').lower() == 'plan':
                plan_list_id = lst.get('id')

        url = f"https://api.pyrus.com/v4/lists/{plan_list_id}/tasks"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        params = {
            'include_archived': 'y',
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        tasks = [self.get_task(task.get('id')) for task in response_data.get('tasks', [])]
        return tasks

    @http_error_decorator
    def get_inbox(self):
        url = "https://api.pyrus.com/v4/inbox"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        inbox_tasks = response_data.get('tasks')
        return inbox_tasks

    @http_error_decorator
    def get_contacts(self):
        '''возвращает список доступных пользователю контактов'''
        url = "https://api.pyrus.com/v4/contacts"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        organizations = response_data.get('organizations')
        persons = organizations[0].get('persons')
        return persons

    @http_error_decorator
    def update_task(self, task_id, **kwargs):
        url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.post(url, headers=headers, json=kwargs)
        response.raise_for_status()
        return response.json()

    def fetch_related_tasks(self, task):
        related_task_ids = task.get('linked_task_ids')
        if not related_task_ids:
            return
        related_tasks = [self.get_task(task_id) for task_id in related_task_ids]
        return related_tasks

    @http_error_decorator
    def locate_plan_list(self):
        '''Возвращает ID списка "Plan"'''
        url = "https://api.pyrus.com/v4/lists"
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        lists = response_data.get('lists', [])
        for lst in lists:
            if lst.get('name', '') == 'Plan':
                return lst.get('id')

    def clear_plan_list(self):
        '''Очищает список "Plan"'''
        tasks = self.get_planed_tasks()
        plan_list_id = self.locate_plan_list()
        for task in tasks:
            self.update_task(task.get('id'), removed_list_ids=[plan_list_id])
